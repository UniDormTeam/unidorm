import csv
import io
import os

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError as DRFValidationError

from accounts.serializers import create_imported_student
from accounts.models import User, StudentProfile

from .models import (
    Organization,
    OrganizationManager,
    OrganizationMembership,
)
from .serializers import (
    OrganizationSerializer,
    AssignManagerSerializer,
    OrganizationManagerSerializer,
    StudentImportRowSerializer,
    AddMemberSerializer,
    OrganizationMemberSerializer,
)
from .permissions import (
    IsSystemAdmin,
    IsManagerOrSystemAdmin,
    IsOrgManagerOrAdmin,
)


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer

    search_fields = ["name", "description", "location"]

    filterset_fields = ["is_active"]

    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManagerOrSystemAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Organization.objects.all()

        return Organization.objects.filter(
            Q(manager_assignments__manager=user)
            | Q(memberships__user=user)
        ).distinct()

    def perform_create(self, serializer):
        organization = serializer.save()
        user = self.request.user

        if user.role == User.Role.MANAGER and not user.is_superuser:
            OrganizationManager.objects.get_or_create(
                organization=organization,
                manager=user,
            )


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Organization.objects.all()

        return Organization.objects.filter(
            Q(manager_assignments__manager=user)
            | Q(memberships__user=user)
        ).distinct()

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsOrgManagerOrAdmin()]

        if self.request.method == "DELETE":
            return [IsSystemAdmin()]

        return [IsAuthenticated()]

    def perform_update(self, serializer):
        serializer.save()


class OrganizationMembersView(generics.ListCreateAPIView):

    permission_classes = [IsOrgManagerOrAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddMemberSerializer
        return OrganizationMemberSerializer

    def get_queryset(self):
        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"],
        )

        return organization.memberships.select_related(
            "user",
            "user__student_profile",
        ).order_by("joined_at")

    def create(self, request, *args, **kwargs):
        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"],
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save(organization=organization)

        user = result["user"]
        profile = getattr(user, "student_profile", None)

        return Response(
            {
                "student_number": profile.student_number if profile else "",
                "username": user.username,
                "full_name": user.get_full_name() or user.username,
                "user_id": user.pk,

                "created_account": result["created_account"],

                "already_member": result["already_member"],
            },
            status=status.HTTP_201_CREATED,
        )


class RemoveMemberView(APIView):

    permission_classes = [IsOrgManagerOrAdmin]

    def delete(self, request, organization_id, member_id):
        membership = get_object_or_404(
            OrganizationMembership,
            pk=member_id,
            organization_id=organization_id,
        )

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignManagerView(APIView):
    permission_classes = [IsOrgManagerOrAdmin]

    def get(self, request, organization_id):
        organization = get_object_or_404(
            Organization,
            pk=organization_id,
        )

        assignments = organization.manager_assignments.select_related(
            "manager"
        )

        serializer = OrganizationManagerSerializer(
            assignments,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request, organization_id):
        organization = get_object_or_404(
            Organization,
            pk=organization_id,
        )

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
    permission_classes = [IsOrgManagerOrAdmin]

    def delete(self, request, organization_id, manager_id):
        assignment = get_object_or_404(
            OrganizationManager,
            organization_id=organization_id,
            manager_id=manager_id,
        )

        assignment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


def _column_key(value):
    text = str(value).replace("\u200c", " ")
    return " ".join(text.split()).lower()


# نام‌های مجاز هر ستون در فایل ورودی؛ هم انگلیسی هم فارسی پذیرفته می‌شود
# هر ستون دیگری در فایل نادیده گرفته می‌شود تا اضافه بودن ستون‌ها خطا ندهد.
COLUMN_ALIASES = {
    _column_key("student_number"): "student_number",
    _column_key("شماره دانشجویی"): "student_number",
    _column_key("شماره دانشجو"): "student_number",
    _column_key("دانشجویی"): "student_number",

    _column_key("first_name"): "first_name",
    _column_key("نام"): "first_name",

    _column_key("last_name"): "last_name",
    _column_key("نام خانوادگی"): "last_name",
    _column_key("نام خانوادگي"): "last_name", 

    _column_key("room_number"): "room_number",
    _column_key("شماره اتاق"): "room_number",
    _column_key("اتاق"): "room_number",

    _column_key("dormitory_name"): "dormitory_name",
    _column_key("نام خوابگاه"): "dormitory_name",
    _column_key("خوابگاه"): "dormitory_name",

    _column_key("building"): "building",
    _column_key("ساختمان"): "building",
    _column_key("بلوک"): "building",

    _column_key("is_dorm_resident"): "is_dorm_resident",
    _column_key("ساکن خوابگاه"): "is_dorm_resident",
}

RESIDENT_TRUE_VALUES = {"1", "true", "yes", "y", "بله", "درست"}
RESIDENT_FALSE_VALUES = {"0", "false", "no", "n", "خیر", "نخیر", "غلط"}


def normalize_import_row(row):
    """
    یک ردیف فایل ورودی را به شکل استاندارد سریالایزر می‌رساند:
    """

    normalized = {}

    for key, value in row.items():
        if key is None:
            continue

        name = COLUMN_ALIASES.get(_column_key(key))

        if name is None or name in normalized:
            continue

        if value is None:
            value = ""

        if isinstance(value, float) and value.is_integer():
            value = int(value)

        if isinstance(value, bool):
            normalized[name] = value
            continue

        normalized[name] = str(value).strip()

    resident = normalized.get("is_dorm_resident")

    if resident is None or resident == "":
        normalized["is_dorm_resident"] = True
    elif isinstance(resident, str):
        token = resident.lower()

        if token in RESIDENT_TRUE_VALUES:
            normalized["is_dorm_resident"] = True
        elif token in RESIDENT_FALSE_VALUES:
            normalized["is_dorm_resident"] = False

    return normalized


class ImportStudentsView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id):
        organization = get_object_or_404(
            Organization,
            pk=organization_id,
        )

        if not request.user.is_superuser:
            is_manager = OrganizationManager.objects.filter(
                organization=organization,
                manager=request.user,
            ).exists()

            if not is_manager:
                return Response(
                    {"detail": "شما اجازه واردسازی دانشجو به این سازمان را ندارید."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"detail": "فایل را با نام file ارسال کنید."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        extension = os.path.splitext(uploaded_file.name)[1].lower()

        try:
            if extension == ".csv":
                content = uploaded_file.read().decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)

            elif extension == ".xlsx":
                from openpyxl import load_workbook

                workbook = load_workbook(
                    uploaded_file,
                    read_only=True,
                    data_only=True,
                )
                worksheet = workbook.active
                values = worksheet.iter_rows(values_only=True)

                headers = next(values, None)

                if not headers:
                    return Response(
                        {"detail": "فایل Excel خالی است."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                headers = [
                    str(header).strip() if header is not None else ""
                    for header in headers
                ]

                rows = [
                    dict(zip(headers, row))
                    for row in values
                    if any(value is not None for value in row)
                ]

                workbook.close()

            else:
                return Response(
                    {"detail": "فقط فایل‌های CSV و XLSX پشتیبانی می‌شوند."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (UnicodeDecodeError, csv.Error, OSError, ValueError) as exc:
            return Response(
                {"detail": f"خواندن فایل ناموفق بود: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not rows:
            return Response(
                {"detail": "هیچ ردیفی برای واردسازی پیدا نشد."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rows = [normalize_import_row(row) for row in rows]

        created_count = 0
        existing_membership_count = 0
        errors = []

        for row_number, row in enumerate(rows, start=2):
            serializer = StudentImportRowSerializer(data=row)

            if not serializer.is_valid():
                errors.append({
                    "row": row_number,
                    "errors": serializer.errors,
                })
                continue

            data = serializer.validated_data

            try:
                student_number = str(data["student_number"]).strip()

                existing_user = User.objects.filter(
                    username=student_number,
                    role=User.Role.STUDENT,
                ).first()

                existing_profile = StudentProfile.objects.filter(
                    student_number=student_number,
                ).first()

                if existing_user or existing_profile:
                    if (
                        not existing_user
                        or not existing_profile
                        or existing_profile.user_id != existing_user.id
                    ):
                        errors.append({
                            "row": row_number,
                            "errors": {
                                "student_number": [
                                    "اطلاعات حساب و پروفایل این شماره دانشجویی با هم سازگار نیستند."
                                ]
                            },
                        })
                        continue

                    with transaction.atomic():
                        _, membership_created = (
                            OrganizationMembership.objects.get_or_create(
                                organization=organization,
                                user=existing_user,
                            )
                        )

                    if membership_created:
                        created_count += 1
                    else:
                        existing_membership_count += 1

                    continue

                with transaction.atomic():
                    student = create_imported_student(data)

                    OrganizationMembership.objects.create(
                        organization=organization,
                        user=student,
                    )

                created_count += 1

            except (DRFValidationError, DjangoValidationError, IntegrityError) as exc:
                errors.append({
                    "row": row_number,
                    "errors": str(exc),
                })

        return Response(
            {
                "organization_id": organization.id,
                "created_or_added": created_count,
                "already_member": existing_membership_count,
                "error_count": len(errors),
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )
