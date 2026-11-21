"""ویوهای مدیریت سازمان‌ها، اعضا و مدیران سازمان."""

import csv
import io
import os

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.exceptions import ValidationError as DRFValidationError

from accounts.models import User
from accounts.serializers import ImportedStudentSerializer, create_imported_student

from .models import Organization, OrganizationManager, OrganizationMembership
from .permissions import (
    IsManagerOrSystemAdmin,
    IsOrgManagerOrAdmin,
    IsOrgMemberOrManager,
)
from .serializers import (
    AddMemberSerializer,
    AssignManagerSerializer,
    OrganizationManagerSerializer,
    OrganizationMemberSerializer,
    OrganizationSerializer,
)


def organizations_for_user(user):
    """
    سازمان‌هایی که کاربر به آن‌ها دسترسی دارد.

    ادمین کل: همه سازمان‌ها
    مدیر: سازمان‌هایی که به او تخصیص داده شده
    دانشجو/مسئول: سازمان‌هایی که عضویت فعال دارند
    """
    if user.is_superuser:
        return Organization.objects.all()

    if user.role == User.Role.MANAGER:
        return Organization.objects.filter(manager_assignments__manager=user)

    return Organization.objects.filter(memberships__user=user, memberships__is_active=True)


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/organizations/   سازمان‌های من
    POST /api/organizations/   ساخت سازمان جدید (مدیر یا ادمین)
    """

    serializer_class = OrganizationSerializer
    search_fields = ("name", "description", "location")
    ordering_fields = ("name", "created_at")
    ordering = ("name",)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsManagerOrSystemAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return organizations_for_user(self.request.user).distinct()

    def perform_create(self, serializer):
        organization = serializer.save()

        # سازنده سازمان (اگر مدیر است) به‌عنوان مدیر همان سازمان ثبت می‌شود
        user = self.request.user
        if user.role == User.Role.MANAGER:
            OrganizationManager.objects.get_or_create(
                organization=organization,
                manager=user,
            )


class OrganizationDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/organizations/{id}/   مشاهده اطلاعات سازمان
    PATCH /api/organizations/{id}/   ویرایش (فقط مدیر همان سازمان)
    """

    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return organizations_for_user(self.request.user).distinct()

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsAuthenticated(), IsOrgManagerOrAdmin()]
        return [IsAuthenticated(), IsOrgMemberOrManager()]


class OrganizationMembersView(generics.ListCreateAPIView):
    """
    GET  /api/organizations/{id}/members/?role=student
    POST /api/organizations/{id}/members/   افزودن یک عضو
    """

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddMemberSerializer
        return OrganizationMemberSerializer

    def get_queryset(self):
        organization = get_object_or_404(Organization, pk=self.kwargs["organization_id"])
        queryset = organization.memberships.select_related(
            "user",
            "user__student_profile",
        ).order_by("user__last_name", "user__username")

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role=role)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = get_object_or_404(
            Organization, pk=self.kwargs["organization_id"]
        )
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()

        return Response(
            {
                "membership_id": membership.pk,
                "account_status": getattr(
                    membership, "account_status", "EXISTING_ATTACHED"
                ),
                "user": {
                    "id": membership.user.pk,
                    "username": membership.user.username,
                    "full_name": membership.user.full_name,
                },
                "membership_role": membership.role,
                "membership_role_display": membership.get_role_display(),
                "room_number": membership.room_number,
            },
            status=status.HTTP_201_CREATED,
        )


class BulkAddMembersView(APIView):
    """
    POST /api/organizations/{id}/members/bulk/

    ثبت گروهی اعضا با JSON. هر ردیف مستقل اعتبارسنجی می‌شود و در صورت
    خطا بقیه ردیف‌ها ثبت می‌شوند؛ نتیجه هر ردیف در results/errors می‌آید.
    """

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        members = request.data.get("members")

        if not isinstance(members, list) or not members:
            raise DRFValidationError({
                "members": "فهرست اعضا الزامی است."
            })

        results = []
        errors = []

        for index, member_data in enumerate(members, start=1):
            serializer = AddMemberSerializer(
                data=member_data,
                context={"organization": organization, "request": request},
            )

            if not serializer.is_valid():
                errors.append({"row": index, "data": member_data, "errors": serializer.errors})
                continue

            try:
                with transaction.atomic():
                    membership = serializer.save()
            except Exception as exc:  # خطای غیرمنتظره یک ردیف بقیه را متوقف نکند
                errors.append({"row": index, "data": member_data, "errors": str(exc)})
                continue

            results.append({
                "membership_id": membership.pk,
                "username": membership.user.username,
                "full_name": membership.user.full_name,
                "membership_role": membership.role,
                "status": getattr(membership, "account_status", "EXISTING_ATTACHED"),
            })

        return Response(
            {
                "summary": {
                    "total_processed": len(members),
                    "created": len(results),
                    "failed_count": len(errors),
                },
                "results": results,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )


class RemoveMemberView(APIView):
    """DELETE /api/organizations/{id}/members/{member_id}/"""

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]

    def delete(self, request, organization_id, member_id):
        membership = get_object_or_404(
            OrganizationMembership,
            pk=member_id,
            organization_id=organization_id,
        )
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignManagerView(APIView):
    """
    GET  /api/organizations/{id}/managers/   فهرست مدیران سازمان
    POST /api/organizations/{id}/managers/   تعیین مدیر (کاربر باید نقش مدیر داشته باشد)
    """

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]

    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        assignments = organization.manager_assignments.select_related("manager")
        return Response(
            OrganizationManagerSerializer(assignments, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        serializer = AssignManagerSerializer(
            data=request.data,
            context={"organization": organization},
        )
        serializer.is_valid(raise_exception=True)
        assignment = serializer.save()

        return Response(
            OrganizationManagerSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


class RemoveManagerView(APIView):
    """DELETE /api/organizations/{id}/managers/{manager_id}/"""

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]

    def delete(self, request, organization_id, manager_id):
        assignment = get_object_or_404(
            OrganizationManager,
            pk=manager_id,
            organization_id=organization_id,
        )
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# ایمپورت دانشجو از فایل CSV یا اکسل
# ---------------------------------------------------------------------------
COLUMN_ALIASES = {
    "student_number": "student_number",
    "شماره دانشجویی": "student_number",
    "شماره_دانشجویی": "student_number",
    "first_name": "first_name",
    "نام": "first_name",
    "last_name": "last_name",
    "نام خانوادگی": "last_name",
    "نام_خانوادگی": "last_name",
    "room_number": "room_number",
    "شماره اتاق": "room_number",
    "شماره_اتاق": "room_number",
    "building": "building",
    "ساختمان": "building",
    "dormitory_name": "dormitory_name",
    "خوابگاه": "dormitory_name",
    "is_dorm_resident": "is_dorm_resident",
    "ساکن": "is_dorm_resident",
}

TRUE_VALUES = {"1", "true", "yes", "y", "بله", "دارد", "ساکن"}
FALSE_VALUES = {"0", "false", "no", "n", "خیر", "ندارد"}


def _column_key(name):
    """نرمال‌سازی نام ستون فایل (حذف فاصله و یکسان‌سازی)."""
    return str(name).strip().lower().replace("ي", "ی").replace("ك", "ک")


def normalize_import_row(raw_row):
    """تبدیل هر ردیف فایل به دیکشنری با کلیدهای استاندارد."""
    row = {}

    for key, value in raw_row.items():
        mapped = COLUMN_ALIASES.get(_column_key(key))
        if not mapped:
            continue

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        if mapped == "is_dorm_resident":
            text = str(value).strip().lower() if value is not None else ""
            row[mapped] = text in TRUE_VALUES
        else:
            row[mapped] = str(value).strip() if value is not None else ""

    return row


class ImportStudentsView(APIView):
    """
    POST /api/organizations/{id}/import-students/

    آپلود فایل CSV یا XLSX با ستون‌های شماره دانشجویی، نام، نام خانوادگی،
    شماره اتاق و ... . هر ردیف یا حساب جدید می‌سازد یا به حساب موجود
    متصل می‌شود.
    """

    permission_classes = [IsAuthenticated, IsOrgManagerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        upload = request.FILES.get("file")

        if not upload:
            return Response(
                {"detail": "فایل اکسل یا CSV را در فیلد file ارسال کنید."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        extension = os.path.splitext(upload.name)[1].lower()

        try:
            if extension == ".csv":
                content = upload.read().decode("utf-8-sig")
                rows = list(csv.DictReader(io.StringIO(content)))
            elif extension in (".xlsx", ".xlsm"):
                import openpyxl

                workbook = openpyxl.load_workbook(upload, read_only=True, data_only=True)
                worksheet = workbook.active
                values = list(worksheet.iter_rows(values_only=True))
                if not values:
                    rows = []
                else:
                    headers = [str(header or "").strip() for header in values[0]]
                    rows = [
                        dict(zip(headers, row))
                        for row in values[1:]
                        if any(cell is not None for cell in row)
                    ]
                workbook.close()
            else:
                return Response(
                    {"detail": "فقط فایل CSV یا XLSX پشتیبانی می‌شود."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (UnicodeDecodeError, OSError, ValueError) as exc:
            return Response(
                {"detail": f"خواندن فایل ناموفق بود: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        errors = []

        for index, raw_row in enumerate(rows, start=2):  # ۲ چون سطر اول عنوان است
            data = normalize_import_row(raw_row)
            serializer = ImportedStudentSerializer(data=data)

            if not serializer.is_valid():
                errors.append({"row": index, "errors": serializer.errors})
                continue

            try:
                with transaction.atomic():
                    user, created = create_imported_student(serializer.validated_data)
                    OrganizationMembership.objects.get_or_create(
                        organization=organization,
                        user=user,
                        defaults={
                            "role": OrganizationMembership.Role.STUDENT,
                            "room_number": serializer.validated_data.get("room_number", ""),
                        },
                    )
            except Exception as exc:
                errors.append({"row": index, "errors": str(exc)})
                continue

            results.append({
                "username": user.username,
                "full_name": user.full_name,
                "status": "CREATED_AND_ATTACHED" if created else "EXISTING_ATTACHED",
            })

        return Response(
            {
                "summary": {
                    "total_processed": len(rows),
                    "created": len(results),
                    "failed_count": len(errors),
                },
                "results": results,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )
