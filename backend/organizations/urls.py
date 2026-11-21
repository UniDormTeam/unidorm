from django.urls import path

from .views import (
    AssignManagerView,
    BulkAddMembersView,
    ImportStudentsView,
    OrganizationDetailView,
    OrganizationListCreateView,
    OrganizationMembersView,
    RemoveMemberView,
    RemoveManagerView,
)

app_name = "organizations"

urlpatterns = [
    # سازمان‌های من / ساخت سازمان
    path("organizations/", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path("organizations/<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),

    # مدیران سازمان
    path(
        "organizations/<int:organization_id>/managers/",
        AssignManagerView.as_view(),
        name="organization-managers",
    ),
    path(
        "organizations/<int:organization_id>/managers/<int:manager_id>/",
        RemoveManagerView.as_view(),
        name="organization-manager-remove",
    ),

    # اعضای سازمان
    path(
        "organizations/<int:organization_id>/members/",
        OrganizationMembersView.as_view(),
        name="organization-members",
    ),
    path(
        "organizations/<int:organization_id>/members/bulk/",
        BulkAddMembersView.as_view(),
        name="organization-members-bulk",
    ),
    path(
        "organizations/<int:organization_id>/members/<int:member_id>/",
        RemoveMemberView.as_view(),
        name="organization-member-remove",
    ),

    # افزودن گروهی دانشجو با فایل CSV/XLSX
    path(
        "organizations/<int:organization_id>/import-students/",
        ImportStudentsView.as_view(),
        name="organization-import-students",
    ),
]
