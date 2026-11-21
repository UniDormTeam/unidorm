from django.conf import settings
from django.db import models


class Organization(models.Model):
    """یک ساختمان/بلوک خوابگاه؛ مرز اصلی جداسازی داده‌ها."""

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "سازمان"
        verbose_name_plural = "سازمان‌ها"
        ordering = ["name"]


class OrganizationManager(models.Model):
    """
    اتصال مدیر به سازمان.

    یک مدیر می‌تواند چند سازمان داشته باشد؛ رابطه جدا نگه داشته شده
    تا دسترسی مدیر به هر سازمان مستقل بررسی شود.
    """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="manager_assignments",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_assignments",
        limit_choices_to={"role": "manager"},
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "manager"],
                name="unique_organization_manager",
            )
        ]
        verbose_name = "مدیر سازمان"
        verbose_name_plural = "مدیران سازمان"

    def __str__(self):
        return f"{self.organization.name} - {self.manager}"


class OrganizationMembership(models.Model):
    """
    عضویت غیرمدیر در سازمان (دانشجو، مسئول تأسیسات یا مسئول اینترنت).

    role داخل عضویت نگه داشته می‌شود چون ممکن است یک کاربر در یک
    سازمان دانشجو و در سازمان دیگر مسئول اینترنت باشد.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "دانشجو"
        FACILITIES = "facilities", "مسئول تأسیسات"
        INTERNET = "internet", "مسئول اینترنت"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    room_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_organization_membership",
            )
        ]
        verbose_name = "عضویت سازمان"
        verbose_name_plural = "عضویت‌های سازمان"

    def __str__(self):
        return f"{self.organization.name} - {self.user} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username
