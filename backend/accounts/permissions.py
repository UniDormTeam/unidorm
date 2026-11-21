from rest_framework.permissions import BasePermission

from .models import User


class IsSystemAdmin(BasePermission):
    """فقط ادمین کل جنگو."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsManager(BasePermission):
    """فقط کاربری که نقش اصلی‌اش مدیر است."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == User.Role.MANAGER
        )


class IsStudent(BasePermission):
    """فقط کاربر با نقش دانشجو."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role == User.Role.STUDENT
        )


class IsStaffMember(BasePermission):
    """مسئول تأسیسات یا اینترنت."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role in (User.Role.FACILITIES, User.Role.INTERNET)
        )
