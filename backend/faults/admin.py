from django.contrib import admin

from .models import MaintenanceRating, MaintenanceRequest, MaintenanceUpdate


class MaintenanceUpdateInline(admin.TabularInline):
    """نمایش تایم‌لاین پیگیری داخل صفحه هر درخواست."""

    model = MaintenanceUpdate
    extra = 0
    readonly_fields = ("author", "status", "category", "note", "created_at")
    can_delete = False


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "room_number",
        "title",
        "category",
        "status",
        "assigned_to",
        "reporter",
        "created_at",
    )
    list_filter = ("category", "status", "organization")
    search_fields = (
        "title",
        "description",
        "room_number",
        "reporter__username",
        "reporter__first_name",
        "reporter__last_name",
    )
    autocomplete_fields = ["organization", "reporter", "assigned_to"]
    readonly_fields = ("room_order", "created_at", "updated_at", "resolved_at")
    inlines = [MaintenanceUpdateInline]


@admin.register(MaintenanceRating)
class MaintenanceRatingAdmin(admin.ModelAdmin):
    list_display = ("request", "reviewer", "score", "created_at")
    list_filter = ("score",)
    search_fields = ("request__title", "reviewer__username", "comment")
