from django.contrib import admin

from .models import Organization, OrganizationManager, OrganizationMembership


class OrganizationManagerInline(admin.TabularInline):
    model = OrganizationManager
    extra = 1
    autocomplete_fields = ["manager"]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "location")
    inlines = [OrganizationManagerInline]


@admin.register(OrganizationManager)
class OrganizationManagerAdmin(admin.ModelAdmin):
    list_display = ("organization", "manager", "assigned_at")
    list_filter = ("organization",)
    search_fields = (
        "organization__name",
        "manager__username",
        "manager__first_name",
        "manager__last_name",
    )
    autocomplete_fields = ["organization", "manager"]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "joined_at")
    list_filter = ("organization",)
    search_fields = (
        "organization__name",
        "user__username",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ["organization", "user"]