from django.db import models
from django.conf import settings


class Organization(models.Model):

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

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships",
        limit_choices_to={"role": "student"},
    )

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
        return f"{self.organization.name} - {self.user}"
