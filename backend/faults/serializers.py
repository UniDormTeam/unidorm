"""سریالایزرهای اعلام خرابی، تایم‌لاین پیگیری و امتیازدهی."""

import os

from django.db import transaction
from rest_framework import serializers

from accounts.models import StudentProfile, User
from organizations.models import Organization, OrganizationMembership

from .models import MaintenanceRating, MaintenanceRequest, MaintenanceUpdate

# حداکثر حجم عکس خرابی (۵ مگابایت)
MAX_IMAGE_SIZE = 5 * 1024 * 1024

# پسوندهای مجاز عکس
ALLOWED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


class MaintenanceRatingSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRating
        fields = ("id", "score", "comment", "reviewer_name", "created_at")
        read_only_fields = fields

    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name() or obj.reviewer.username


class MaintenanceUpdateSerializer(serializers.ModelSerializer):
    """یک ردیف تایم‌لاین؛ همه فیلدها خواندنی هستند."""

    author_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = MaintenanceUpdate
        fields = (
            "id",
            "author",
            "author_name",
            "status",
            "status_display",
            "category",
            "category_display",
            "note",
            "created_at",
        )
        read_only_fields = fields

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """نمایش کامل درخواست برای دانشجو، مدیر و مسئولین."""

    organization_name = serializers.CharField(source="organization.name", read_only=True)
    reporter_name = serializers.SerializerMethodField()
    reporter_username = serializers.CharField(source="reporter.username", read_only=True)
    student_number = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    updates = MaintenanceUpdateSerializer(many=True, read_only=True)
    rating = MaintenanceRatingSerializer(read_only=True)
    has_rating = serializers.SerializerMethodField()
    can_be_rated = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRequest
        fields = (
            "id",
            "organization",
            "organization_name",
            "reporter",
            "reporter_name",
            "reporter_username",
            "student_number",
            "title",
            "description",
            "room_number",
            "image",
            "category",
            "category_display",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "manager_note",
            "updates",
            "rating",
            "has_rating",
            "can_be_rated",
            "created_at",
            "updated_at",
            "resolved_at",
        )
        read_only_fields = fields

    def get_reporter_name(self, obj):
        return obj.reporter.get_full_name() or obj.reporter.username

    def get_student_number(self, obj):
        try:
            return obj.reporter.student_profile.student_number
        except StudentProfile.DoesNotExist:
            return ""

    def get_assigned_to_name(self, obj):
        if not obj.assigned_to:
            return ""
        return obj.assigned_to.get_full_name() or obj.assigned_to.username

    def get_has_rating(self, obj):
        return hasattr(obj, "rating")

    def get_can_be_rated(self, obj):
        """فقط ثبت‌کننده و فقط درخواست انجام‌شده بدون امتیاز."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return (
            obj.reporter_id == request.user.id
            and obj.status == MaintenanceRequest.Status.RESOLVED
            and not hasattr(obj, "rating")
        )


class CreateMaintenanceRequestSerializer(serializers.ModelSerializer):
    """
    ثبت درخواست جدید توسط دانشجو.

    organization در مسیر سازمانی از URL خوانده می‌شود؛ در مسیر شخصی
    (/api/maintenance-requests/) باید در بدنه ارسال شود.
    """

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True),
        required=False,
    )
    category = serializers.ChoiceField(choices=MaintenanceRequest.Category.choices)
    room_number = serializers.CharField(max_length=20, required=False, allow_blank=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = MaintenanceRequest
        fields = ("organization", "title", "description", "category", "room_number", "image")

    def validate_room_number(self, value):
        return value.strip()

    def validate_image(self, value):
        if not value:
            return value

        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("حجم عکس نباید بیشتر از ۵ مگابایت باشد.")

        extension = os.path.splitext(value.name)[1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise serializers.ValidationError(
                "فقط عکس با پسوند JPG، PNG، GIF یا WebP پذیرفته می‌شود."
            )

        return value

    def validate(self, attrs):
        user = self.context["request"].user

        # در مسیر سازمانی، سازمان همیشه از URL خوانده می‌شود و کاربر
        # نمی‌تواند با فرستادن organization در بدنه، مسیر را عوض کند.
        url_organization = self.context.get("organization")
        body_organization = attrs.get("organization")

        if url_organization and body_organization and (
            url_organization.pk != body_organization.pk
        ):
            raise serializers.ValidationError({
                "organization": "سازمان درخواست با آدرس آن هم‌خوان نیست."
            })

        organization = url_organization or body_organization

        if organization is None:
            raise serializers.ValidationError({"organization": "سازمان الزامی است."})

        if not organization.is_active:
            raise serializers.ValidationError({"organization": "این سازمان غیرفعال است."})

        is_member = OrganizationMembership.objects.filter(
            organization=organization,
            user=user,
            is_active=True,
        ).exists()

        if not (user.is_superuser or is_member):
            raise serializers.ValidationError({
                "organization": "شما عضو این سازمان نیستید."
            })

        room_number = attrs.get("room_number")

        if not room_number:
            room_number = self._profile_room_number(user)

            if not room_number:
                raise serializers.ValidationError({
                    "room_number": (
                        "شماره اتاق برای شما ثبت نشده است؛ آن را در همین درخواست "
                        "وارد کنید یا از مدیر سازمان بخواهید ثبت کند."
                    )
                })

            attrs["room_number"] = room_number

        attrs["organization"] = organization
        return attrs

    @staticmethod
    def _profile_room_number(user):
        if user.role != User.Role.STUDENT:
            return ""

        try:
            return user.student_profile.room_number.strip()
        except StudentProfile.DoesNotExist:
            return ""

    @transaction.atomic
    def create(self, validated_data):
        maintenance_request = MaintenanceRequest.objects.create(**validated_data)
        maintenance_request.add_update(
            author=self.context["request"].user,
            note="ثبت اعلام خرابی",
        )
        return maintenance_request


class UpdateMaintenanceRequestSerializer(serializers.ModelSerializer):
    """PATCH مدیر: دسته‌بندی، وضعیت، ارجاع و توضیح."""

    class Meta:
        model = MaintenanceRequest
        fields = ("category", "status", "assigned_to", "manager_note")

    def validate_assigned_to(self, value):
        if value is None:
            return value

        organization = self.instance.organization
        is_valid_staff = OrganizationMembership.objects.filter(
            organization=organization,
            user=value,
            is_active=True,
            role__in=[
                OrganizationMembership.Role.FACILITIES,
                OrganizationMembership.Role.INTERNET,
            ],
        ).exists()

        if not is_valid_staff:
            raise serializers.ValidationError(
                "فقط مسئول تأسیسات یا اینترنت همین سازمان قابل انتخاب است."
            )

        return value

    def validate(self, attrs):
        """نقش مسئول انتخاب‌شده باید با دسته نهایی درخواست هم‌خوان باشد."""
        assigned_to = attrs.get("assigned_to")
        category = attrs.get("category", self.instance.category)

        if assigned_to and category in (
            MaintenanceRequest.Category.FACILITIES,
            MaintenanceRequest.Category.INTERNET,
        ):
            membership = OrganizationMembership.objects.filter(
                organization=self.instance.organization,
                user=assigned_to,
                is_active=True,
            ).first()

            if not membership or membership.role != category:
                raise serializers.ValidationError({
                    "assigned_to": "مسئول انتخاب‌شده با دسته درخواست هم‌خوان نیست."
                })

        return attrs


class MaintenanceActionSerializer(serializers.Serializer):
    """
    بدنه ثبت رسیدگی (POST .../updates/).

    مدیر می‌تواند وضعیت، دسته و مسئول را تغییر دهد؛ مسئول تأسیسات/اینترنت
    فقط وضعیت انجام‌شده/نامرتبط و توضیح را تغییر می‌دهد.
    """

    new_status = serializers.ChoiceField(
        choices=MaintenanceRequest.Status.choices,
        required=False,
    )
    category = serializers.ChoiceField(
        choices=MaintenanceRequest.Category.choices,
        required=False,
    )
    assigned_to_id = serializers.IntegerField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)


class MaintenanceNoteSerializer(serializers.Serializer):
    """یادداشت ساده روی درخواست (مسیر سازگاری)."""

    note = serializers.CharField(allow_blank=False)


class RatingCreateSerializer(serializers.Serializer):
    """ثبت امتیاز و نظر دانشجو."""

    score = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True)
