from rest_framework.permissions import BasePermission

from organizations.models import OrganizationManager, OrganizationMembership

from .models import MaintenanceRequest


# ---------------------------------------------------------------------------
# توابع کمکی مجوز (در ویوها هم استفاده می‌شوند)
# ---------------------------------------------------------------------------
def is_org_manager(user, organization):
    """آیا کاربر مدیر همین سازمان است (یا ادمین کل)؟"""
    if not (user and user.is_authenticated):
        return False

    if user.is_superuser:
        return True

    return OrganizationManager.objects.filter(
        organization=organization,
        manager=user,
    ).exists()


def get_membership(user, organization):
    """عضویت فعال کاربر در سازمان (اگر وجود داشته باشد)."""
    if not (user and user.is_authenticated):
        return None

    return OrganizationMembership.objects.filter(
        organization=organization,
        user=user,
        is_active=True,
    ).first()


def is_org_staff(user, organization):
    """مسئول تأسیسات یا اینترنت همین سازمان."""
    membership = get_membership(user, organization)
    return bool(
        membership
        and membership.role
        in (
            OrganizationMembership.Role.FACILITIES,
            OrganizationMembership.Role.INTERNET,
        )
    )


def can_handle_request(user, maintenance_request):
    """
    چه کسی می‌تواند وضعیت درخواست را تغییر دهد؟

    - مدیر همان سازمان: همه درخواست‌ها
    - مسئول تأسیسات/اینترنت: درخواست ارجاع‌شده به خودش یا هم‌دسته با نقشش
    """
    if is_org_manager(user, maintenance_request.organization):
        return True

    if maintenance_request.assigned_to_id == user.id:
        return True

    membership = get_membership(user, maintenance_request.organization)

    if not membership:
        return False

    # نقش مسئول با دسته درخواست باید هم‌خوان باشد
    return membership.role == maintenance_request.category


def can_view_request(user, maintenance_request):
    """دانشجوی ثبت‌کننده، مدیر سازمان یا مسئول مربوطه."""
    if not (user and user.is_authenticated):
        return False

    if user.is_superuser or maintenance_request.reporter_id == user.id:
        return True

    return can_handle_request(user, maintenance_request)


# ---------------------------------------------------------------------------
# کلاس‌های Permission
# ---------------------------------------------------------------------------
class IsOrganizationManager(BasePermission):
    """مدیر سازمانی که در URL آمده است."""

    def has_permission(self, request, view):
        organization_id = view.kwargs.get("organization_id")
        if organization_id is None:
            return False

        from organizations.models import Organization

        organization = Organization.objects.filter(pk=organization_id).first()
        return bool(organization and is_org_manager(request.user, organization))


class IsOrganizationMember(BasePermission):
    """عضویت فعال در سازمانی که در URL آمده است (برای ثبت درخواست)."""

    def has_permission(self, request, view):
        from organizations.models import Organization

        organization_id = view.kwargs.get("organization_id")
        organization = Organization.objects.filter(pk=organization_id).first()

        return bool(
            organization and get_membership(request.user, organization)
        )


class CanViewOrganizationFaults(BasePermission):
    """مدیر یا مسئول (تأسیسات/اینترنت) سازمان برای دیدن لیست درخواست‌ها."""

    def has_permission(self, request, view):
        from organizations.models import Organization

        organization_id = view.kwargs.get("organization_id")
        organization = Organization.objects.filter(pk=organization_id).first()

        if not organization:
            return False

        return bool(
            is_org_manager(request.user, organization)
            or is_org_staff(request.user, organization)
        )


class IsRequestHandler(BasePermission):
    """تغییر وضعیت: مدیر سازمان یا مسئول مربوطه."""

    def has_object_permission(self, request, view, obj):
        return can_handle_request(request.user, obj)


class IsRequestManager(BasePermission):
    """تغییر دسته/ارجاع/تأیید و رد: فقط مدیر سازمان."""

    def has_object_permission(self, request, view, obj):
        return is_org_manager(request.user, obj.organization)


class IsRequestParticipant(BasePermission):
    """یادداشت روی درخواست: ثبت‌کننده، مدیر یا مسئول مربوطه."""

    def has_object_permission(self, request, view, obj):
        if obj.reporter_id == request.user.id:
            return True
        return can_handle_request(request.user, obj)


class IsRequestReporter(BasePermission):
    """لغو/امتیاز فقط برای دانشجوی ثبت‌کننده (یا ادمین کل)."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or obj.reporter_id == user.id)
        )
