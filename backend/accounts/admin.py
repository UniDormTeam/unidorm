from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ManagerProfile, StudentProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """افزودن ستون نقش و شماره تماس به پنل ادمین."""

    list_display = (
        "username",
        "first_name",
        "last_name",
        "role",
        "phone_number",
        "is_active",
    )
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "phone_number")

    # فیلدهای نقش و شماره تماس در فرم ویرایش کاربر
    fieldsets = UserAdmin.fieldsets + (
        ("اطلاعات تکمیلی", {"fields": ("role", "phone_number")}),
    )

    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     ("اطلاعات سامانه", {
    #         "fields": ("role", "phone_number"),
    #     }),
    # )


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "national_code", "job_title")
    search_fields = ("user__username", "national_code")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "student_number",
        "is_dorm_resident",
        "dormitory_name",
        "building",
        "room_number",
    )
    list_filter = ("is_dorm_resident", "building")
    search_fields = ("user__username", "student_number", "room_number")
