from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import User, ManagerProfile, StudentProfile


class ManagerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ManagerProfile
        fields = ("national_code", "job_title")
        read_only_fields = fields


class StudentProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentProfile
        fields = (
            "student_number",
            "is_dorm_resident",
            "dormitory_name",
            "building",
            "room_number",
        )
        read_only_fields = fields


class MeSerializer(serializers.ModelSerializer):

    manager_profile = ManagerProfileSerializer(read_only=True)
    student_profile = StudentProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "manager_profile",
            "student_profile",
        ]
        read_only_fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "role",
            "manager_profile",
            "student_profile",
        ]


class AdminCreateUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        validators=[validate_password],
    )

    #  مدیر
    national_code = serializers.CharField(
        write_only=True,
        required=False,
    )
    job_title = serializers.CharField(
        write_only=True,
        required=False,
    )

    #  دانشجو
    student_number = serializers.CharField(
        write_only=True,
        required=False,
    )
    is_dorm_resident = serializers.BooleanField(
        write_only=True,
        required=False,
        default=False,
    )
    dormitory_name = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        default="",
    )
    building = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        default="",
    )
    room_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        default="",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "national_code",
            "job_title",
            "student_number",
            "is_dorm_resident",
            "dormitory_name",
            "building",
            "room_number",
        )
        read_only_fields = ("id",)

    def validate_national_code(self, value):

        if not value.isascii() or not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "کد ملی باید دقیقاً ۱۰ رقم باشد."
            )

        if ManagerProfile.objects.filter(
            national_code=value
        ).exists():
            raise serializers.ValidationError(
                "این کد ملی قبلاً ثبت شده است."
            )

        return value

    def validate_student_number(self, value):

        if StudentProfile.objects.filter(
            student_number=value
        ).exists():
            raise serializers.ValidationError(
                "این شماره دانشجویی قبلاً ثبت شده است."
            )

        return value

    def validate(self, attrs):

        role = attrs.get("role")

        if role == User.Role.MANAGER:
            missing = {}

            if not attrs.get("national_code"):
                missing["national_code"] = "کد ملی مدیر الزامی است."

            if not attrs.get("job_title"):
                missing["job_title"] = "سمت مدیر الزامی است."

            if missing:
                raise serializers.ValidationError(missing)

            student_fields = (
                "student_number",
                "is_dorm_resident",
                "dormitory_name",
                "building",
                "room_number",
            )

            for field in student_fields:
                if field in self.initial_data:
                    raise serializers.ValidationError({
                        field: "این فیلد مخصوص دانشجو است."
                    })

        elif role == User.Role.STUDENT:
            if not attrs.get("student_number"):
                raise serializers.ValidationError({
                    "student_number": "شماره دانشجویی الزامی است."
                })

            if attrs.get("national_code") or attrs.get("job_title"):
                raise serializers.ValidationError(
                    "اطلاعات اختصاصی مدیر برای دانشجو مجاز نیست."
                )

            if not attrs.get("is_dorm_resident", False):
                attrs["dormitory_name"] = ""
                attrs["building"] = ""
                attrs["room_number"] = ""

            else:
                if not attrs.get("dormitory_name").strip():
                    raise serializers.ValidationError({
                        "dormitory_name": "نام خوابگاه الزامی است."
                    })

                if not attrs.get("building").strip():
                    raise serializers.ValidationError({
                        "building": "ساختمان الزامی است."
                    })

                if not attrs.get("room_number").strip():
                    raise serializers.ValidationError({
                        "room_number": "شماره اتاق الزامی است."
                    })

        else:
            raise serializers.ValidationError({
                "role": "نقش باید مدیر یا دانشجو باشد."
            })

        return attrs
 

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data["role"]

        if role == User.Role.MANAGER:
            profile_data = {
                "national_code": validated_data.pop("national_code"),
                "job_title": validated_data.pop("job_title"),
            }

            for field in (
                "student_number",
                "is_dorm_resident",
                "dormitory_name",
                "building",
                "room_number",
            ):
                validated_data.pop(field, None)

        else:
            profile_data = {
                "student_number": validated_data.pop("student_number"),
                "is_dorm_resident": validated_data.pop(
                    "is_dorm_resident", False
                ),
                "dormitory_name": validated_data.pop(
                    "dormitory_name", ""
                ),
                "building": validated_data.pop("building", ""),
                "room_number": validated_data.pop("room_number", ""),
            }

            validated_data.pop("national_code", None)
            validated_data.pop("job_title", None)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if role == User.Role.MANAGER:
            profile = ManagerProfile(
                user=user,
                **profile_data,
            )
        else:
            profile = StudentProfile(
                user=user,
                **profile_data,
            )

        try:
            profile.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)

        profile.save()

        return user




class ImportedStudentSerializer(serializers.Serializer):
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



@transaction.atomic
def create_imported_student(data):
    student_number = str(data["student_number"]).strip()

    if not student_number:
        raise serializers.ValidationError({
            "student_number": "شماره دانشجویی الزامی است."
        })

    if User.objects.filter(username=student_number).exists():
        raise serializers.ValidationError({
            "student_number": "برای این شماره دانشجویی حساب کاربری وجود دارد."
        })

    if StudentProfile.objects.filter(
        student_number=student_number
    ).exists():
        raise serializers.ValidationError({
            "student_number": "این شماره دانشجویی قبلاً ثبت شده است."
        })

    is_dorm_resident = data.get("is_dorm_resident", True)

    dormitory_name = data.get("dormitory_name", "").strip()
    building = data.get("building", "").strip()
    room_number = data.get("room_number", "").strip()

    if not is_dorm_resident:
        dormitory_name = ""
        building = ""
        room_number = ""

    user = User(
        username=student_number,
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        role=User.Role.STUDENT,
    )

    user.set_password(student_number)
    user.save()

    profile = StudentProfile(
        user=user,
        student_number=student_number,
        is_dorm_resident=is_dorm_resident,
        dormitory_name=dormitory_name,
        building=building,
        room_number=room_number,
    )

    try:
        profile.full_clean()
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.message_dict)

    profile.save()

    return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    تغییر رمز عبور کاربر فعلی (اختیاری).
    """

    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("رمز عبور فعلی اشتباه است.")

        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

        return value

    def validate(self, attrs):
        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError({
                "new_password": "رمز جدید باید با رمز فعلی متفاوت باشد."
            })

        return attrs


class ManagerRegisterSerializer(AdminCreateUserSerializer):
    """
     ثبت‌نام آزاد مدیر — بدون تأیید ادمین.
    """

    role = serializers.ChoiceField(
        choices=User.Role.choices,
        required=False,
    )

    def validate(self, attrs):
        requested_role = self.initial_data.get("role")

        if requested_role is not None and requested_role != User.Role.MANAGER:
            raise serializers.ValidationError({
                "role": (
                    "ثبت‌نام آزاد فقط برای مدیران است؛ "
                    "حساب دانشجو را مدیر سازمان می‌سازد."
                )
            })

        attrs["role"] = User.Role.MANAGER

        return super().validate(attrs)

