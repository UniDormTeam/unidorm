from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from organizations.models import Organization


def room_sort_value(room_number):
    """شماره اتاق را برای مرتب‌سازی عددی به عدد تبدیل می‌کند."""
    digits = "".join(
        character for character in str(room_number) if character.isdecimal()
    )

    return int(digits) if digits else 0


class MaintenanceRequest(models.Model):

    class Category(models.TextChoices):
        # چهار دسته اصلی MVP
        REPAIRS = "repairs", "تعمیرات"
        FACILITIES = "facilities", "تأسیسات"
        INTERNET = "internet", "اینترنت"
        OTHER = "other", "متفرقه"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "ثبت‌شده"
        APPROVED = "approved", "تأییدشده"
        IN_PROGRESS = "in_progress", "در حال پیگیری"
        RESOLVED = "resolved", "انجام‌شده"
        REJECTED = "rejected", "ردشده"
        IRRELEVANT = "irrelevant", "نامرتبط"
        CANCELLED = "cancelled", "لغو‌شده"

    # وضعیت‌هایی که درخواست در آن‌ها بسته محسوب می‌شود
    CLOSED_STATUSES = (
        Status.RESOLVED,
        Status.REJECTED,
        Status.IRRELEVANT,
        Status.CANCELLED,
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="maintenance_requests",
    )

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maintenance_requests",
        limit_choices_to={"role": "student"},
    )

    # مسئول رسیدگی (مسئول تأسیسات یا اینترنت) که مدیر ارجاع می‌دهد
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_maintenance_requests",
        blank=True,
        null=True,
    )

    title = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    room_number = models.CharField(max_length=20)

    room_order = models.IntegerField(default=0)

    category = models.CharField(
        max_length=15,
        choices=Category.choices,
        default=Category.OTHER,
    )

    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    manager_note = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="maintenance/%Y/%m/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    resolved_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.room_order = room_sort_value(self.room_number)

        # زمان بسته‌شدن درخواست را خودکار نگه می‌داریم
        if self.status == self.Status.RESOLVED and self.resolved_at is None:
            self.resolved_at = timezone.now()
        elif self.status != self.Status.RESOLVED:
            self.resolved_at = None

        super().save(*args, **kwargs)

    def add_update(self, author, note=""):
        """ثبت یک ردیف در تایم‌لاین پیگیری با وضعیت فعلی درخواست."""
        return MaintenanceUpdate.objects.create(
            request=self,
            author=author,
            category=self.category,
            status=self.status,
            note=note,
        )

    @property
    def is_closed(self):
        return self.status in self.CLOSED_STATUSES

    def __str__(self):
        return f"{self.organization.name} - اتاق {self.room_number} - {self.title}"

    class Meta:
        verbose_name = "درخواست تعمیر"
        verbose_name_plural = "درخواست‌های تعمیر"
        ordering = ["-created_at"]


class MaintenanceUpdate(models.Model):
    """هر تغییر وضعیت/دسته/ارجاع یا یادداشت، یک ردیف تایم‌لاین می‌سازد."""

    request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name="updates",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maintenance_updates",
    )

    status = models.CharField(
        max_length=15,
        choices=MaintenanceRequest.Status.choices,
    )

    category = models.CharField(
        max_length=15,
        choices=MaintenanceRequest.Category.choices,
    )

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_id} - {self.get_status_display()}"

    class Meta:
        verbose_name = "به‌روزرسانی درخواست"
        verbose_name_plural = "به‌روزرسانی‌های درخواست"
        ordering = ["created_at"]


class MaintenanceRating(models.Model):
    """امتیاز و نظر دانشجو پس از انجام‌شدن درخواست."""

    request = models.OneToOneField(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name="rating",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="maintenance_ratings",
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_id} - {self.score}/5"

    class Meta:
        verbose_name = "امتیاز درخواست"
        verbose_name_plural = "امتیازهای درخواست"
