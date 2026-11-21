from rest_framework.permissions import BasePermission

from accounts.models import User

from .models import OrganizationManager, OrganizationMembership


class IsManagerOrSystemAdmin(BasePermission):
    """ساخت سازمان فقط برای مدیر یا ادمین کل."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role == User.Role.MANAGER)
        )


class IsOrgManagerOrAdmin(BasePermission):
    """
    مدیر همان سازمان (از URL) یا ادمین کل.

    سازمان همیشه از URL خوانده می‌شود تا کاربر نتواند آیدی سازمان دیگری
    را در بدنه درخواست جایگزین کند.
    """

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        if user.is_superuser:
            return True

        organization_id = view.kwargs.get("organization_id") or view.kwargs.get(
            "pk"
        )

        if organization_id is None:
            return False

        return OrganizationManager.objects.filter(
            organization_id=organization_id,
            manager=user,
        ).exists()


class IsOrgMemberOrManager(BasePermission):
    """هر عضو فعال سازمان یا مدیر همان سازمان (برای مشاهده اطلاعات)."""

    def has_permission(self, request, view):
        user = request.user

        if not (user and user.is_authenticated):
            return False

        if user.is_superuser:
            return True

        organization_id = view.kwargs.get("organization_id") or view.kwargs.get(
            "pk"
        )

        if organization_id is None:
            return False

        if OrganizationManager.objects.filter(
            organization_id=organization_id,
            manager=user,
        ).exists():
            return True

        return OrganizationMembership.objects.filter(
            organization_id=organization_id,
            user=user,
            is_active=True,
        ).exists()
