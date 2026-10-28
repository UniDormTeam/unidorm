from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


# username
# first_name
# last_name
# email
# password

class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = "manager", "مدیر"
        STUDENT = "student", "دانشجو"

    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
    )

    def __str__(self):
        return self.get_full_name() or self.username


class ManagerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="manager_profile",
        limit_choices_to={"role": User.Role.MANAGER},
    )

    national_code = models.CharField(
        max_length=10,
        unique=True,
    )

    job_title = models.CharField(max_length=100)

    def clean(self):
        super().clean()

        if self.user_id and self.user.role != User.Role.MANAGER:
            raise ValidationError({
                "user": "پروفایل مدیر فقط برای کاربران با نقش مدیر است."
            })

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.job_title}"


class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": User.Role.STUDENT},
    )

    student_number = models.CharField(
        max_length=20,
        unique=True,
    )

    is_dorm_resident = models.BooleanField(default=False)

    dormitory_name = models.CharField(
        max_length=100,
        blank=True,
    )

    building = models.CharField(
        max_length=50,
        blank=True,
    )

    room_number = models.CharField(
        max_length=20,
        blank=True,
    )
    
    def clean(self):
        super().clean()

        if self.user_id and self.user.role != User.Role.STUDENT:
            raise ValidationError({
                "user": "پروفایل دانشجو فقط برای کاربران با نقش دانشجو است."
            })

        if not self.is_dorm_resident:
            if self.dormitory_name or self.building or self.room_number:
                raise ValidationError(
                    "برای دانشجوی غیرساکن خوابگاه، اطلاعات خوابگاه باید خالی باشد."
                )


    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.student_number}"
