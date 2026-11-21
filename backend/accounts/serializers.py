"""سریالایزرهای حساب کاربری: ورود، ثبت‌نام مدیر، پروفایل و ساخت کاربر."""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import ManagerProfile, StudentProfile, User
from .utils import build_organizations_payload, build_profile_payload


class LoginSerializer(serializers.Serializer):
    """فقط اعتبارسنجی ورودی است؛ بررسی رمز در View انجام می‌شود."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ManagerRegisterSerializer(serializers.Serializer):
    """ثبت‌نام مدیر (درگاه عمومی). نقش همیشه manager تنظیم می‌شود."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    job_title = serializers.CharField(max_length=100)
    national_code = serializers.CharField(max_length=10)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return value

    def validate_national_code(self, value):
        # کد ملی در این MVP فقط ۱۰ رقم عددی است
        if not (value.isascii() and value.isdigit() and len(value) == 10):
            raise serializers.ValidationError("کد ملی باید ۱۰ رقم عددی باشد.")
        if ManagerProfile.objects.filter(national_code=value).exists():
            raise serializers.ValidationError("این کد ملی قبلاً ثبت شده است.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email", ""),
            phone_number=validated_data.get("phone_number", ""),
            role=User.Role.MANAGER,
        )
        ManagerProfile.objects.create(
            user=user,
            national_code=validated_data["national_code"],
            job_title=validated_data["job_title"],
        )
        return user


class MeSerializer(serializers.ModelSerializer):
    """پروفایل کاربر جاری؛ فرانت‌اند برای نمایش حساب از این استفاده می‌کند."""

    profile = serializers.SerializerMethodField()
    organizations = serializers.SerializerMethodField()
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "role",
            "role_display",
            "profile",
            "organizations",
        )
        # نقش و نام کاربری قابل تغییر از این مسیر نیستند
        read_only_fields = ("id", "username", "role", "role_display")

    def get_profile(self, obj):
        return build_profile_payload(obj)

    def get_organizations(self, obj):
        return build_organizations_payload(obj)


class AdminCreateUserSerializer(serializers.Serializer):
    """ساخت حساب توسط ادمین کل (برای مدیر، دانشجو یا مسئولین)."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=User.Role.choices)

    # فیلدهای مخصوص مدیر
    national_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    job_title = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # فیلدهای مخصوص دانشجو
    student_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    is_dorm_resident = serializers.BooleanField(required=False, default=False)
    dormitory_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    building = serializers.CharField(max_length=50, required=False, allow_blank=True)
    room_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        role = attrs["role"]

        if role == User.Role.MANAGER:
            if not attrs.get("national_code") or not attrs.get("job_title"):
                raise serializers.ValidationError({
                    "detail": "برای مدیر، کد ملی و عنوان شغلی الزامی است."
                })

        if role == User.Role.STUDENT:
            if not attrs.get("student_number"):
                raise serializers.ValidationError({
                    "detail": "برای دانشجو، شماره دانشجویی الزامی است."
                })
            if StudentProfile.objects.filter(
                student_number=attrs["student_number"]
            ).exists():
                raise serializers.ValidationError({
                    "student_number": "این شماره دانشجویی قبلاً ثبت شده است."
                })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data["role"]

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email", ""),
            phone_number=validated_data.get("phone_number", ""),
            role=role,
        )

        if role == User.Role.MANAGER:
            ManagerProfile.objects.create(
                user=user,
                national_code=validated_data["national_code"],
                job_title=validated_data["job_title"],
            )

        if role == User.Role.STUDENT:
            StudentProfile.objects.create(
                user=user,
                student_number=validated_data["student_number"],
                is_dorm_resident=validated_data.get("is_dorm_resident", False),
                dormitory_name=validated_data.get("dormitory_name", ""),
                building=validated_data.get("building", ""),
                room_number=validated_data.get("room_number", ""),
            )

        return user


class ChangePasswordSerializer(serializers.Serializer):
    """تغییر رمز توسط خود کاربر."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی صحیح نیست.")
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value, self.context["request"].user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": "رمز جدید باید با رمز فعلی متفاوت باشد."
            })
        return attrs


class ImportedStudentSerializer(serializers.Serializer):
    """یک ردیف دانشجو برای افزودن گروهی (اکسل/CSV یا JSON)."""

    student_number = serializers.CharField(max_length=20)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    is_dorm_resident = serializers.BooleanField(required=False, default=False)
    dormitory_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    building = serializers.CharField(max_length=50, required=False, allow_blank=True)
    room_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_student_number(self, value):
        return value.strip()


def create_imported_student(data):
    """
    ساخت (یا استفاده از) حساب دانشجو و پروفایل او.

    اگر حسابی با همان شماره دانشجویی وجود داشته باشد، فقط پروفایلش
    تکمیل می‌شود و حساب تکراری ساخته نمی‌شود. رمز پیش‌فرض حساب‌های
    جدید همان شماره دانشجویی است.
    """
    student_number = data["student_number"].strip()

    existing = User.objects.filter(username=student_number).first()

    if existing and existing.role != User.Role.STUDENT:
        raise serializers.ValidationError(
            f"کاربر «{student_number}» وجود دارد ولی نقش او دانشجو نیست."
        )

    created = False

    if existing:
        user = existing
    else:
        user = User(
            username=student_number,
            role=User.Role.STUDENT,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )
        user.set_password(student_number)  # رمز پیش‌فرض
        user.save()
        created = True

    StudentProfile.objects.update_or_create(
        user=user,
        defaults={
            "student_number": student_number,
            "is_dorm_resident": data.get("is_dorm_resident", False),
            "dormitory_name": data.get("dormitory_name", ""),
            "building": data.get("building", ""),
            "room_number": data.get("room_number", ""),
        },
    )

    return user, created
