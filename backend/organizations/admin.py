from django.contrib import admin

from .models import Organization, OrganizationManager, OrganizationMembership


class OrganizationManagerInline(admin.TabularInline):
    model = OrganizationManager
    extra = 0
    autocomplete_fields = ("manager",)


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "location")
    inlines = [OrganizationManagerInline, OrganizationMembershipInline]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "room_number", "is_active")
    list_filter = ("role", "is_active", "organization")
    search_fields = ("user__username", "user__first_name", "user__last_name", "room_number")
    autocomplete_fields = ("organization", "user")
