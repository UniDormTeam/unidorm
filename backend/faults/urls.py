from django.urls import path

from .views import (
    MaintenanceActionView,
    MaintenanceCancelView,
    MaintenanceRateView,
    MaintenanceRequestDetailView,
    MaintenanceRequestListCreateView,
    MaintenanceUpdateNoteView,
    OrganizationMaintenanceRequestsView,
    PersonalMaintenanceDetailView,
)

app_name = "faults"

urlpatterns = [
    # ------------------------------------------------------------------
    # مسیرهای شخصی دانشجو
    # ------------------------------------------------------------------
    path(
        "maintenance-requests/",
        MaintenanceRequestListCreateView.as_view(),
        name="maintenance-request-list-create",
    ),
    path(
        "maintenance-requests/<int:pk>/",
        PersonalMaintenanceDetailView.as_view(),
        name="maintenance-request-detail",
    ),
    path(
        "maintenance-requests/<int:pk>/updates/",
        MaintenanceUpdateNoteView.as_view(),
        name="maintenance-request-updates",
    ),
    path(
        "maintenance-requests/<int:pk>/cancel/",
        MaintenanceCancelView.as_view(),
        name="maintenance-request-cancel",
    ),

    # ------------------------------------------------------------------
    # مسیرهای داخل سازمان (مدیر / مسئول تأسیسات / مسئول اینترنت)
    # ------------------------------------------------------------------
    path(
        "organizations/<int:organization_id>/maintenance-requests/",
        OrganizationMaintenanceRequestsView.as_view(),
        name="organization-maintenance-requests",
    ),
    path(
        "organizations/<int:organization_id>/maintenance-requests/<int:pk>/",
        MaintenanceRequestDetailView.as_view(),
        name="organization-maintenance-request-detail",
    ),
    path(
        "organizations/<int:organization_id>/maintenance-requests/<int:pk>/updates/",
        MaintenanceActionView.as_view(),
        name="organization-maintenance-request-updates",
    ),
    path(
        "organizations/<int:organization_id>/maintenance-requests/<int:pk>/rate/",
        MaintenanceRateView.as_view(),
        name="organization-maintenance-request-rate",
    ),
]
