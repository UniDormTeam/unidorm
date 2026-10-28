from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, ManagerProfile, StudentProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
    )

    list_filter = ("role", "is_active", "is_staff")
    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )

    fieldsets = UserAdmin.fieldsets + (
        ("اطلاعات سامانه", {
            "fields": ("role", "phone_number"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("اطلاعات سامانه", {
            "fields": ("role", "phone_number"),
        }),
    )


@admin.register(ManagerProfile)
class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "national_code", "job_title")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "national_code",
    )


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

    list_filter = ("is_dorm_resident", "dormitory_name")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "student_number",
    )
