from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import StudentProfile
from accounts.serializers import create_imported_student

from .models import Organization, OrganizationManager, OrganizationMembership

User = get_user_model()


class OrganizationManagerSerializer(serializers.ModelSerializer):

    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationManager
        fields = ("id", "manager", "manager_name", "assigned_at")
        read_only_fields = ("id", "manager_name", "assigned_at")

    def get_manager_name(self, obj):
        return obj.manager.get_full_name() or obj.manager.username


class OrganizationSerializer(serializers.ModelSerializer):

    managers = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "description",
            "location",
            "is_active",
            "created_at",
            "updated_at",
            "managers",
        )
        read_only_fields = ("id", "created_at", "updated_at", "managers")

    def get_managers(self, obj):
        assignments = obj.manager_assignments.select_related("manager")
        return OrganizationManagerSerializer(assignments, many=True).data


class AssignManagerSerializer(serializers.ModelSerializer):

    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="manager")
    )

    class Meta:
        model = OrganizationManager
        fields = ("manager",)

    def validate(self, attrs):
        organization = self.context["organization"]
        manager = attrs["manager"]

        if OrganizationManager.objects.filter(
            organization=organization,
            manager=manager,
        ).exists():
            raise serializers.ValidationError(
                {"manager": "این مدیر قبلاً به این سازمان اختصاص داده شده است."}
            )

        return attrs

    def create(self, validated_data):
        return OrganizationManager.objects.create(
            organization=self.context["organization"],
            **validated_data,
        )


class StudentImportRowSerializer(serializers.Serializer):
    """اعتبارسنجی اطلاعات یک دانشجو از فایل ورودی."""

    student_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    is_dorm_resident = serializers.BooleanField(default=True)

    dormitory_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )
    building = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )
    room_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default="",
    )


class AddMemberSerializer(serializers.Serializer):
    """
    دو حالت :
    یا از قبل دانشجو اکانت داره و فقط عضو سازمان میشه 
    یا براش اکانت میسازه با رمز پیشفرض و عضو سازمان میشه
    """

    student_number = serializers.CharField(max_length=20)

    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default="",
    )

    is_dorm_resident = serializers.BooleanField(required=False, default=True)
    dormitory_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )
    building = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        default="",
    )
    room_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default="",
    )

    def validate_student_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("شماره دانشجویی الزامی است.")

        return value


    def validate(self, attrs):
        student_number = attrs["student_number"]
        self._existing_user = self._find_account(student_number)

        if self._existing_user is None:
            # حسابی با این شماره هست ولی پروفایلش ناهماهنگ است
            has_user = User.objects.filter(username=student_number).exists()
            has_profile = StudentProfile.objects.filter(
                student_number=student_number,
            ).exists()

            if has_user or has_profile:
                raise serializers.ValidationError({
                    "student_number": (
                        "اطلاعات حساب و پروفایل این شماره دانشجویی "
                        "با هم سازگار نیستند."
                    ),
                })

            if not attrs.get("first_name") or not attrs.get("last_name"):
                raise serializers.ValidationError({
                    "first_name": (
                        "برای ساخت حساب جدید، نام و نام خانوادگی الزامی است."
                    ),
                })

        return attrs

    @staticmethod
    def _find_account(student_number):
        """
        حسابی که مالک این شماره دانشجویی است را پیدا می‌کند.
        """
        user = User.objects.filter(username=student_number).first()
        profile = StudentProfile.objects.filter(
            student_number=student_number,
        ).first()

        if user and profile and profile.user_id == user.pk:
            return user

        return None

    def save(self, organization, **kwargs):
        """عضو کردن دانشجو در سازمان؛ با حساب موجود یا ساخت حساب تازه."""
        data = self.validated_data
        existing_user = self._existing_user

        # حالت ۱:
        if existing_user is not None:
            _, membership_created = OrganizationMembership.objects.get_or_create(
                organization=organization,
                user=existing_user,
            )

            return {
                "user": existing_user,
                "created_account": False,
                "already_member": not membership_created,
            }

        # حالت ۲:
        user = create_imported_student({
            "student_number": data["student_number"],
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "is_dorm_resident": data["is_dorm_resident"],
            "dormitory_name": data["dormitory_name"],
            "building": data["building"],
            "room_number": data["room_number"],
        })

        OrganizationMembership.objects.get_or_create(
            organization=organization,
            user=user,
        )

        return {
            "user": user,
            "created_account": True,
            "already_member": False,
        }


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """نمایش یک عضو دانشجوی سازمان در فهرست اعضا."""

    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    student_number = serializers.SerializerMethodField()
    room_number = serializers.SerializerMethodField()
    dormitory_name = serializers.SerializerMethodField()
    building = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "user",
            "username",
            "full_name",
            "student_number",
            "room_number",
            "dormitory_name",
            "building",
            "joined_at",
        )
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_username(self, obj):
        return obj.user.username

    def _profile(self, obj):
        return getattr(obj.user, "student_profile", None)

    def get_student_number(self, obj):
        profile = self._profile(obj)
        return profile.student_number if profile else ""

    def get_room_number(self, obj):
        profile = self._profile(obj)
        return profile.room_number if profile else ""

    def get_dormitory_name(self, obj):
        profile = self._profile(obj)
        return profile.dormitory_name if profile else ""

    def get_building(self, obj):
        profile = self._profile(obj)
        return profile.building if profile else ""
