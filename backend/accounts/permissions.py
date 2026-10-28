from rest_framework.permissions import BasePermission
from .models import User



class IsSystemAdmin(BasePermission):
    """فقط ادمین کل سامانه اجازه دسترسی دارد."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsManager(BasePermission):
    """فقط کاربران دارای نقش مدیر."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.MANAGER
        )


class IsStudent(BasePermission):
    """فقط کاربران دارای نقش دانشجو."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.STUDENT
        )
