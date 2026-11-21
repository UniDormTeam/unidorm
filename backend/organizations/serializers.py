"""سریالایزرهای سازمان، مدیران سازمان و اعضا."""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.models import StudentProfile, User
from accounts.serializers import ImportedStudentSerializer, create_imported_student

from .models import Organization, OrganizationManager, OrganizationMembership


class OrganizationManagerSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationManager
        fields = ("id", "organization", "manager", "manager_name", "assigned_at")
        read_only_fields = ("id", "organization", "manager_name", "assigned_at")

    def get_manager_name(self, obj):
        return obj.manager.get_full_name() or obj.manager.username


class OrganizationSerializer(serializers.ModelSerializer):
    managers = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "description",
            "location",
            "is_active",
            "managers",
            "stats",
            "my_role",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "managers", "stats", "my_role", "created_at", "updated_at")

    def get_managers(self, obj):
        assignments = obj.manager_assignments.select_related("manager")
        return OrganizationManagerSerializer(assignments, many=True).data

    def get_stats(self, obj):
        """آمار کوتاه برای کارت سازمان در پنل مدیریت."""
        memberships = obj.memberships.filter(is_active=True)
        return {
            "total_members": memberships.count(),
            "total_students": memberships.filter(
                role=OrganizationMembership.Role.STUDENT
            ).count(),
            "total_staff": memberships.filter(
                role__in=[
                    OrganizationMembership.Role.FACILITIES,
                    OrganizationMembership.Role.INTERNET,
                ]
            ).count(),
            # درخواست‌های باز = همه به‌جز وضعیت‌های پایانی
            "open_faults": obj.maintenance_requests.exclude(
                status__in=["resolved", "rejected", "irrelevant", "cancelled"]
            ).count(),
        }

    def get_my_role(self, obj):
        """
        نقش کاربر جاری در این سازمان:
        manager / student / facilities / internet / none
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return "none"

        user = request.user

        if user.is_superuser:
            return "admin"

        if obj.manager_assignments.filter(manager=user).exists():
            return "manager"

        membership = obj.memberships.filter(user=user, is_active=True).first()
        return membership.role if membership else "none"


class AssignManagerSerializer(serializers.Serializer):
    """تعیین مدیر برای سازمان؛ کاربر باید از قبل حساب مدیر داشته باشد."""

    manager = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(role=User.Role.MANAGER)
    )

    def validate_manager(self, value):
        organization = self.context["organization"]
        if OrganizationManager.objects.filter(
            organization=organization,
            manager=value,
        ).exists():
            raise serializers.ValidationError("این کاربر از قبل مدیر این سازمان است.")
        return value

    def create(self, validated_data):
        return OrganizationManager.objects.create(
            organization=self.context["organization"],
            manager=validated_data["manager"],
        )


class AddMemberSerializer(serializers.Serializer):
    """
    افزودن یک عضو به سازمان.

    اگر حساب کاربری با این username وجود نداشته باشد ساخته می‌شود؛
    رمز پیش‌فرض حساب جدید همان username است. اگر حساب وجود داشته باشد
    فقط عضویت سازمان ایجاد می‌شود (بدون ساخت کاربر تکراری).
    """

    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    membership_role = serializers.ChoiceField(
        choices=OrganizationMembership.Role.choices,
        default=OrganizationMembership.Role.STUDENT,
    )
    room_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    is_dorm_resident = serializers.BooleanField(required=False, default=False)
    dormitory_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    building = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        return value.strip()

    def validate(self, attrs):
        organization = self.context["organization"]
        username = attrs["username"]
        role = attrs["membership_role"]

        existing = User.objects.filter(username=username).first()

        if existing:
            # نقش اصلی حساب باید با نقشی که در سازمان می‌گیرد هم‌خوان باشد
            allowed_roles = {
                OrganizationMembership.Role.STUDENT: {User.Role.STUDENT},
                OrganizationMembership.Role.FACILITIES: {
                    User.Role.FACILITIES,
                    User.Role.STUDENT,
                },
                OrganizationMembership.Role.INTERNET: {
                    User.Role.INTERNET,
                    User.Role.STUDENT,
                },
            }
            if existing.role not in allowed_roles[role]:
                raise serializers.ValidationError({
                    "username": (
                        f"کاربر «{username}» با نقش "
                        f"«{existing.get_role_display()}» وجود دارد و "
                        "نمی‌تواند با این نقش به سازمان اضافه شود."
                    )
                })

        if OrganizationMembership.objects.filter(
            organization=organization,
            user__username=username,
        ).exists():
            raise serializers.ValidationError({
                "username": "این کاربر از قبل عضو این سازمان است."
            })

        attrs["_existing_user"] = existing
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        organization = self.context["organization"]
        role = validated_data["membership_role"]
        existing = validated_data.pop("_existing_user", None)
        username = validated_data["username"]

        account_status = "EXISTING_ATTACHED"

        if existing:
            user = existing
            # اطلاعات تماس جدید را روی حساب موجود به‌روز می‌کنیم
            changed_fields = []
            if validated_data.get("first_name"):
                user.first_name = validated_data["first_name"]
                changed_fields.append("first_name")
            if validated_data.get("last_name"):
                user.last_name = validated_data["last_name"]
                changed_fields.append("last_name")
            if validated_data.get("phone_number"):
                user.phone_number = validated_data["phone_number"]
                changed_fields.append("phone_number")
            if changed_fields:
                user.save(update_fields=changed_fields)
        else:
            account_status = "CREATED_AND_ATTACHED"
            user = User(
                username=username,
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
                phone_number=validated_data.get("phone_number", ""),
                role={
                    OrganizationMembership.Role.STUDENT: User.Role.STUDENT,
                    OrganizationMembership.Role.FACILITIES: User.Role.FACILITIES,
                    OrganizationMembership.Role.INTERNET: User.Role.INTERNET,
                }[role],
            )
            user.set_password(username)  # رمز پیش‌فرض
            user.save()

        # دانشجو پروفایل دانشجویی دارد؛ مسئولین فقط حساب کاربری دارند
        if role == OrganizationMembership.Role.STUDENT:
            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    "student_number": username,
                    "is_dorm_resident": validated_data.get(
                        "is_dorm_resident", False
                    ),
                    "dormitory_name": validated_data.get("dormitory_name", ""),
                    "building": validated_data.get("building", ""),
                    "room_number": validated_data.get("room_number", ""),
                },
            )

        membership = OrganizationMembership.objects.create(
            organization=organization,
            user=user,
            role=role,
            room_number=validated_data.get("room_number", ""),
        )

        # برای اینکه ویو بتواند وضعیت ساخت حساب را در پاسخ برگرداند
        membership.account_status = account_status

        return membership


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """نمایش اعضای سازمان در جدول پنل مدیر."""

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    membership_role = serializers.CharField(source="role", read_only=True)
    membership_role_display = serializers.CharField(
        source="get_role_display",
        read_only=True,
    )
    student_number = serializers.SerializerMethodField()
    dormitory_name = serializers.SerializerMethodField()
    building = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "user_id",
            "username",
            "full_name",
            "phone_number",
            "membership_role",
            "membership_role_display",
            "room_number",
            "student_number",
            "dormitory_name",
            "building",
            "is_active",
            "joined_at",
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def _student_profile(self, obj):
        return getattr(obj.user, "student_profile", None)

    def get_student_number(self, obj):
        profile = self._student_profile(obj)
        return profile.student_number if profile else ""

    def get_dormitory_name(self, obj):
        profile = self._student_profile(obj)
        return profile.dormitory_name if profile else ""

    def get_building(self, obj):
        profile = self._student_profile(obj)
        return profile.building if profile else ""


class BulkAddMemberSerializer(serializers.Serializer):
    """بدنه افزودن گروهی اعضا به سازمان (JSON)."""

    members = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )


# برای ایمپورت اکسل/CSV از همان سریالایزر دانشجوی اکانت استفاده می‌کنیم
__all__ = [
    "AddMemberSerializer",
    "AssignManagerSerializer",
    "BulkAddMemberSerializer",
    "ImportedStudentSerializer",
    "OrganizationManagerSerializer",
    "OrganizationMemberSerializer",
    "OrganizationSerializer",
    "create_imported_student",
]
