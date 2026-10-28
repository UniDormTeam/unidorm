from rest_framework.permissions import BasePermission
from accounts.models import User
from .models import OrganizationManager


class IsManagerOrSystemAdmin(BasePermission):
    """ساخت سازمان برای مدیران و ادمین کل."""

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        return user.is_superuser or user.role == User.Role.MANAGER


class IsOrgManagerOrAdmin(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        if user.is_superuser:
            return True

        organization_id = view.kwargs.get(
            "organization_id",
            view.kwargs.get("pk"),
        )

        if organization_id is None:
            return False

        return OrganizationManager.objects.filter(
            organization_id=organization_id,
            manager=user,
        ).exists()


class IsSystemAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsAssignedManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.manager_assignments.filter(
            manager=request.user
        ).exists()