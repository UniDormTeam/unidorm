from django.urls import path

from .views import (
    OrganizationListCreateView,
    OrganizationDetailView,
    OrganizationMembersView,
    RemoveMemberView,
    AssignManagerView,
    RemoveManagerView,
    ImportStudentsView,
)

app_name = "organizations"

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-list-create"),
    path( "<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("<int:organization_id>/managers/", AssignManagerView.as_view(), name="organization-managers"),
    path("<int:organization_id>/members/", OrganizationMembersView.as_view(), name="organization-members"),
    path("<int:organization_id>/members/<int:member_id>/", RemoveMemberView.as_view(), name="organization-member-remove"),
    path("<int:organization_id>/managers/<int:manager_id>/", RemoveManagerView.as_view(), name="organization-manager-remove"),
    path("<int:organization_id>/import-students/", ImportStudentsView.as_view(), name="organization-import-students"),
]