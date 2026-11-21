from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

# username
# first_name
# last_name
# email
# password

class User(AbstractUser):
    """
    کاربر سامانه.

    نقش کاربر (role) نقش اصلی او در سامانه است و برای هدایت فرانت‌اند به
    داشبورد مناسب استفاده می‌شود. نقش کاربر داخل هر سازمان جداگانه در
    OrganizationMembership ذخیره می‌شود.
    """

    class Role(models.TextChoices):
        MANAGER = "manager", "مدیر"
        STUDENT = "student", "دانشجو"
        FACILITIES = "facilities", "مسئول تأسیسات"
        INTERNET = "internet", "مسئول اینترنت"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        help_text="نقش اصلی کاربر در سامانه",
    )

    # برای همه نقش‌ها (به‌ویژه مسئول تأسیسات/اینترنت) شماره تماس نگه می‌داریم
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_facilities(self):
        return self.role == self.Role.FACILITIES

    @property
    def is_internet(self):
        return self.role == self.Role.INTERNET


class ManagerProfile(models.Model):
    """اطلاعات تکمیلی حساب مدیر."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="manager_profile",
        limit_choices_to={"role": User.Role.MANAGER},
    )
    national_code = models.CharField(max_length=10, unique=True)
    job_title = models.CharField(max_length=100)

    def clean(self):
        super().clean()

        if self.user_id and self.user.role != User.Role.MANAGER:
            raise ValidationError(
                {"user": "پروفایل مدیر فقط برای کاربران با نقش مدیر است."}
            )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.job_title}"

    class Meta:
        verbose_name = "پروفایل مدیر"
        verbose_name_plural = "پروفایل‌های مدیران"


class StudentProfile(models.Model):
    """اطلاعات دانشجویی و خوابگاهی دانشجو."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": User.Role.STUDENT},
    )
    student_number = models.CharField(max_length=20, unique=True)
    is_dorm_resident = models.BooleanField(default=False)
    dormitory_name = models.CharField(max_length=100, blank=True)
    building = models.CharField(max_length=50, blank=True)
    room_number = models.CharField(max_length=20, blank=True)

    def clean(self):
        super().clean()

        if self.user_id and self.user.role != User.Role.STUDENT:
            raise ValidationError(
                {"user": "پروفایل دانشجو فقط برای کاربران با نقش دانشجو است."}
            )

        if not self.is_dorm_resident and (
            self.dormitory_name or self.building or self.room_number
        ):
            raise ValidationError(
                "برای دانشجوی غیرساکن خوابگاه، اطلاعات خوابگاه باید خالی باشد."
            )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.student_number}"

    class Meta:
        verbose_name = "پروفایل دانشجو"
        verbose_name_plural = "پروفایل‌های دانشجویان"
