"""ساخت پاسخ ورود؛ فرانت‌اند علاوه بر توکن‌ها به این اطلاعات نیاز دارد."""

from organizations.models import OrganizationMembership


def build_profile_payload(user):
    """
    اطلاعات پروفایل متناسب با نقش کاربر.

    دانشجو: اطلاعات خوابگاه و شماره دانشجویی
    مدیر: عنوان شغلی و کد ملی
    مسئول تأسیسات/اینترنت: فقط شماره تماس
    """
    if user.role == user.Role.STUDENT:
        profile = getattr(user, "student_profile", None)
        if profile is None:
            return {}

        return {
            "student_number": profile.student_number,
            "is_dorm_resident": profile.is_dorm_resident,
            "dormitory_name": profile.dormitory_name,
            "building": profile.building,
            "room_number": profile.room_number,
            "phone_number": user.phone_number,
        }

    if user.role == user.Role.MANAGER:
        profile = getattr(user, "manager_profile", None)
        if profile is None:
            return {"phone_number": user.phone_number}

        return {
            "job_title": profile.job_title,
            "national_code": profile.national_code,
            "phone_number": user.phone_number,
        }

    return {"phone_number": user.phone_number}


def build_organizations_payload(user):
    """
    فهرست سازمان‌هایی که کاربر در آن‌ها نقش دارد.

    مدیر: از OrganizationManager خوانده می‌شود.
    دانشجو/تأسیسات/اینترنت: از OrganizationMembership خوانده می‌شود.
    اولین سازمان به‌عنوان سازمان پیش‌فرض علامت‌گذاری می‌شود تا فرانت‌اند
    سازمان فعال اولیه را انتخاب کند.
    """
    entries = []
    seen = set()

    for assignment in user.organization_assignments.select_related(
        "organization"
    ).order_by("organization__name"):
        organization = assignment.organization
        if not organization.is_active or organization.pk in seen:
            continue
        seen.add(organization.pk)
        entries.append(
            {
                "organization_id": organization.pk,
                "organization_name": organization.name,
                "membership_role": "manager",
                "membership_role_display": "مدیر",
                "room_number": "",
            }
        )

    memberships = (
        OrganizationMembership.objects.filter(user=user, is_active=True)
        .select_related("organization")
        .order_by("organization__name")
    )

    for membership in memberships:
        organization = membership.organization
        if not organization.is_active or organization.pk in seen:
            continue
        seen.add(organization.pk)
        entries.append(
            {
                "organization_id": organization.pk,
                "organization_name": organization.name,
                "membership_role": membership.role,
                "membership_role_display": membership.get_role_display(),
                "room_number": membership.room_number,
            }
        )

    for index, entry in enumerate(entries):
        entry["is_default"] = index == 0

    return entries


def build_login_payload(user):
    """پاسخ کامل ورود/ثبت‌نام برای React."""
    organizations = build_organizations_payload(user)

    capabilities = {
        "is_system_admin": user.is_superuser,
        # ساخت/مدیریت سازمان فقط برای مدیر (یا ادمین کل)
        "can_manage_organizations": bool(
            user.is_superuser or user.role == user.Role.MANAGER
        ),
        "can_report_faults": user.role == user.Role.STUDENT,
        # پنل‌هایی که فرانت‌اند باید در منو نشان دهد
        "fault_panels": [
            entry["membership_role"]
            for entry in organizations
            if entry["membership_role"] in ("manager", "facilities", "internet")
        ],
        # بخش نوبت‌دهی فعلاً خارج از MVP است و همیشه خالی برمی‌گردد
        "has_booking_panel": False,
    }

    return {
        "user": {
            "id": user.pk,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
            "role_display": user.get_role_display(),
            "profile": build_profile_payload(user),
        },
        "organizations": organizations,
        # برای سازگاری با قرارداد API؛ در MVP خالی است
        "special_assignments": [],
        "capabilities": capabilities,
    }
