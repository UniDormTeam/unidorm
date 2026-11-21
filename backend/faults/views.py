"""ویوهای اعلام خرابی: ثبت، پیگیری، رسیدگی، ارجاع و امتیازدهی."""

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from organizations.models import Organization, OrganizationMembership

from .models import MaintenanceRating, MaintenanceRequest
from .permissions import (
    CanViewOrganizationFaults,
    IsOrganizationMember,
    IsRequestManager,
    IsRequestReporter,
    can_handle_request,
    can_view_request,
    get_membership,
    is_org_manager,
)
from .serializers import (
    CreateMaintenanceRequestSerializer,
    MaintenanceActionSerializer,
    MaintenanceNoteSerializer,
    MaintenanceRequestSerializer,
    RatingCreateSerializer,
    UpdateMaintenanceRequestSerializer,
)


class MaintenanceOrderingFilter(OrderingFilter):
    """
    مرتب‌سازی ساده برای فرانت‌اند:
        ?ordering=room_number   مرتب‌سازی عددی شماره اتاق
        ?ordering=-created_at   جدیدترین درخواست اول
    """

    ALIASES = {"room_number": "room_order"}

    def get_ordering(self, request, queryset, view):
        ordering = super().get_ordering(request, queryset, view)
        if not ordering:
            return ordering

        mapped = []
        for field in ordering:
            prefix = "-" if field.startswith("-") else ""
            name = field[len(prefix):]
            mapped.append(prefix + self.ALIASES.get(name, name))
        return mapped


FILTER_BACKENDS = [
    SearchFilter,
    DjangoFilterBackend,
    MaintenanceOrderingFilter,
]


def request_queryset():
    """کوئری پایه با روابط مورد نیاز سریالایزر (بدون N+1)."""
    return MaintenanceRequest.objects.select_related(
        "organization",
        "reporter",
        "reporter__student_profile",
        "assigned_to",
    ).prefetch_related("updates", "rating")


def start_request_workflow(maintenance_request, author, note):
    """ثبت ردیف تایم‌لاین و ذخیره وضعیت جدید."""
    maintenance_request.save()
    maintenance_request.add_update(author=author, note=note)


class MaintenanceRequestListCreateView(generics.ListCreateAPIView):
    """
    POST /api/maintenance-requests/       ثبت اعلام خرابی (سازمان در بدنه)
    GET  /api/maintenance-requests/       درخواست‌های خودم
    """

    permission_classes = [IsAuthenticated]
    filter_backends = FILTER_BACKENDS
    filterset_fields = ["status", "category", "organization"]
    search_fields = ["title", "description", "room_number"]
    ordering_fields = ["created_at", "room_number"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateMaintenanceRequestSerializer
        return MaintenanceRequestSerializer

    def get_queryset(self):
        return request_queryset().filter(reporter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        output = MaintenanceRequestSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(output.data),
        )


class OrganizationMaintenanceRequestsView(generics.ListCreateAPIView):
    """
    GET  /api/organizations/{id}/maintenance-requests/
         مدیر: همه درخواست‌ها
         مسئول تأسیسات/اینترنت: فقط دسته خودش یا ارجاع‌شده به خودش

    POST /api/organizations/{id}/maintenance-requests/
         ثبت درخواست جدید توسط دانشجوی عضو سازمان
    """

    filter_backends = FILTER_BACKENDS
    filterset_fields = ["status", "category"]
    search_fields = ["title", "description", "room_number"]
    ordering_fields = ["created_at", "room_number"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsOrganizationMember()]
        return [IsAuthenticated(), CanViewOrganizationFaults()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateMaintenanceRequestSerializer
        return MaintenanceRequestSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = get_object_or_404(
            Organization, pk=self.kwargs["organization_id"]
        )
        return context

    def get_queryset(self):
        organization = get_object_or_404(
            Organization, pk=self.kwargs["organization_id"]
        )
        queryset = request_queryset().filter(organization=organization)
        user = self.request.user

        # مدیر همه درخواست‌های سازمان را می‌بیند
        if is_org_manager(user, organization):
            return queryset

        # مسئول فقط دسته خودش یا درخواست‌های ارجاع‌شده به خودش را می‌بیند
        membership = get_membership(user, organization)
        role = membership.role if membership else None

        return queryset.filter(
            models_q_category_or_assignment(user, role)
        )

    def perform_create(self, serializer):
        organization = self.get_serializer_context()["organization"]
        serializer.save(
            reporter=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        output = MaintenanceRequestSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


def models_q_category_or_assignment(user, role):
    """شرط «دسته برابر نقش من» یا «به من ارجاع شده»."""
    from django.db.models import Q

    return Q(assigned_to=user) | Q(category=role)


class _RequestLookupMixin:
    """پیدا کردن درخواست داخل سازمان مسیر (برای جلوگیری از دسترسی بین‌سازمانی)."""

    def get_request_object(self):
        queryset = request_queryset()

        if "organization_id" in self.kwargs:
            queryset = queryset.filter(organization_id=self.kwargs["organization_id"])

        return get_object_or_404(queryset, pk=self.kwargs["pk"])


class MaintenanceRequestDetailView(_RequestLookupMixin, generics.RetrieveUpdateAPIView):
    """
    GET   /api/organizations/{id}/maintenance-requests/{request_id}/
    PATCH /api/organizations/{id}/maintenance-requests/{request_id}/
          (فقط مدیر: دسته، وضعیت، ارجاع، توضیح)
    """

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [IsAuthenticated(), IsRequestManager()]
        return [IsAuthenticated()]

    def get_object(self):
        maintenance_request = self.get_request_object()

        if self.request.method in ("PUT", "PATCH"):
            self.check_object_permissions(self.request, maintenance_request)
        elif not can_view_request(self.request.user, maintenance_request):
            # برای جلوگیری از افشای وجود درخواست، 404 برمی‌گردانیم
            raise PermissionDenied("شما به این درخواست دسترسی ندارید.")

        return maintenance_request

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateMaintenanceRequestSerializer
        return MaintenanceRequestSerializer

    def perform_update(self, serializer):
        instance = serializer.instance
        before = (
            instance.category,
            instance.status,
            instance.assigned_to_id,
            instance.manager_note,
        )
        maintenance_request = serializer.save()
        after = (
            maintenance_request.category,
            maintenance_request.status,
            maintenance_request.assigned_to_id,
            maintenance_request.manager_note,
        )

        if before != after:
            maintenance_request.add_update(
                author=self.request.user,
                note=maintenance_request.manager_note or "رسیدگی مدیر به درخواست",
            )


class PersonalMaintenanceDetailView(_RequestLookupMixin, generics.RetrieveAPIView):
    """GET /api/maintenance-requests/{id}/ — جزئیات درخواست خودم."""

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        maintenance_request = self.get_request_object()

        if not can_view_request(self.request.user, maintenance_request):
            raise PermissionDenied("شما به این درخواست دسترسی ندارید.")

        return maintenance_request


class MaintenanceActionView(_RequestLookupMixin, APIView):
    """
    POST /api/organizations/{id}/maintenance-requests/{request_id}/updates/

    مدیر: تأیید/رد/در حال پیگیری/انجام‌شده + تغییر دسته + ارجاع
    مسئول تأسیسات/اینترنت: انجام‌شده یا نامرتبط + توضیح
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, organization_id, pk):
        maintenance_request = self.get_request_object()

        if not can_handle_request(request.user, maintenance_request):
            raise PermissionDenied("شما اجازه رسیدگی به این درخواست را ندارید.")

        serializer = MaintenanceActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        manager = is_org_manager(user, maintenance_request.organization)

        new_status = data.get("new_status")
        new_category = data.get("category")
        # وجود کلید مهم است؛ null یعنی برداشتن ارجاع
        has_assignment_change = "assigned_to_id" in data
        assigned_to_id = data.get("assigned_to_id")
        comment = data.get("comment", "")

        # مسئول غیرمدیر فقط می‌تواند کار را تمام/نامرتبط کند
        if not manager:
            allowed = {
                MaintenanceRequest.Status.RESOLVED,
                MaintenanceRequest.Status.IRRELEVANT,
                MaintenanceRequest.Status.IN_PROGRESS,
            }
            if new_status and new_status not in allowed:
                raise PermissionDenied(
                    "مسئول فقط می‌تواند وضعیت را در حال پیگیری، انجام‌شده "
                    "یا نامرتبط کند."
                )
            if new_category or has_assignment_change:
                raise PermissionDenied(
                    "تغییر دسته‌بندی و ارجاع فقط توسط مدیر سازمان انجام می‌شود."
                )

        if new_category:
            maintenance_request.category = new_category

        if has_assignment_change:
            if assigned_to_id is None or assigned_to_id == "":
                maintenance_request.assigned_to = None
            else:
                assigned_user = get_object_or_404(User, pk=assigned_to_id)
                membership = OrganizationMembership.objects.filter(
                    organization=maintenance_request.organization,
                    user=assigned_user,
                    is_active=True,
                    role__in=[
                        OrganizationMembership.Role.FACILITIES,
                        OrganizationMembership.Role.INTERNET,
                    ],
                ).first()

                if not membership:
                    raise ValidationError({
                        "assigned_to_id": (
                            "این کاربر مسئول تأسیسات یا اینترنت این سازمان نیست."
                        )
                    })

                # نقش مسئول باید با دسته نهایی درخواست هم‌خوان باشد
                if maintenance_request.category in (
                    MaintenanceRequest.Category.FACILITIES,
                    MaintenanceRequest.Category.INTERNET,
                ) and membership.role != maintenance_request.category:
                    raise ValidationError({
                        "assigned_to_id": "مسئول انتخاب‌شده با دسته درخواست هم‌خوان نیست."
                    })

                maintenance_request.assigned_to = assigned_user

        if new_status:
            maintenance_request.status = new_status

        if comment:
            maintenance_request.manager_note = comment

        maintenance_request.save()
        maintenance_request.add_update(
            author=user,
            note=comment or f"تغییر وضعیت به {maintenance_request.get_status_display()}",
        )

        return Response(
            MaintenanceRequestSerializer(
                maintenance_request,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )


class MaintenanceUpdateNoteView(_RequestLookupMixin, APIView):
    """
    POST /api/maintenance-requests/{id}/updates/

    یادداشت ساده توسط دانشجوی ثبت‌کننده یا مدیر (مسیر سازگاری).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        maintenance_request = self.get_request_object()

        if not can_view_request(request.user, maintenance_request):
            raise PermissionDenied("شما به این درخواست دسترسی ندارید.")

        if maintenance_request.is_closed:
            raise ValidationError({
                "detail": "این درخواست بسته شده و نمی‌توان روی آن یادداشت گذاشت."
            })

        serializer = MaintenanceNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update = maintenance_request.add_update(
            author=request.user,
            note=serializer.validated_data["note"],
        )

        return Response(
            {
                "id": update.pk,
                "request_id": maintenance_request.pk,
                "status": update.status,
                "note": update.note,
                "author_name": update.author.full_name,
                "created_at": update.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class MaintenanceCancelView(APIView):
    """POST /api/maintenance-requests/{id}/cancel/ — لغو توسط دانشجو."""

    permission_classes = [IsAuthenticated, IsRequestReporter]

    def post(self, request, pk):
        maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
        self.check_object_permissions(request, maintenance_request)

        if maintenance_request.is_closed:
            return Response(
                {"detail": "این درخواست بسته شده و دیگر قابل لغو نیست."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        maintenance_request.status = MaintenanceRequest.Status.CANCELLED
        maintenance_request.save(update_fields=["status", "resolved_at", "updated_at"])
        maintenance_request.add_update(
            author=request.user,
            note="درخواست توسط دانشجو لغو شد",
        )

        return Response(
            MaintenanceRequestSerializer(
                maintenance_request,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )


class MaintenanceRateView(_RequestLookupMixin, APIView):
    """
    POST /api/organizations/{id}/maintenance-requests/{request_id}/rate/

    فقط دانشجوی ثبت‌کننده و فقط برای درخواست انجام‌شده.
    """

    permission_classes = [IsAuthenticated, IsRequestReporter]

    def post(self, request, organization_id, pk):
        maintenance_request = self.get_request_object()
        self.check_object_permissions(request, maintenance_request)

        if maintenance_request.status != MaintenanceRequest.Status.RESOLVED:
            return Response(
                {"detail": "فقط درخواست انجام‌شده قابل امتیازدهی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if hasattr(maintenance_request, "rating"):
            return Response(
                {"detail": "برای این درخواست قبلاً امتیاز ثبت شده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RatingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating = MaintenanceRating.objects.create(
            request=maintenance_request,
            reviewer=request.user,
            score=serializer.validated_data["score"],
            comment=serializer.validated_data.get("comment", ""),
        )

        return Response(
            {
                "id": rating.pk,
                "request_id": maintenance_request.pk,
                "score": rating.score,
                "comment": rating.comment,
                "created_at": rating.created_at,
            },
            status=status.HTTP_201_CREATED,
        )
