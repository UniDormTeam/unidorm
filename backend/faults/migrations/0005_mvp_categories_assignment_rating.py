import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


CATEGORY_MAP = {
    # دسته‌های قدیمی به دسته‌های چهارگانه MVP نگاشت می‌شوند
    "unclassified": "other",
    "contractor": "repairs",
    "technician": "repairs",
}


def forwards(apps, schema_editor):
    """تبدیل داده‌های قدیمی (پیمانکار/تعمیرکار) به دسته‌های جدید."""
    MaintenanceRequest = apps.get_model("faults", "MaintenanceRequest")
    MaintenanceUpdate = apps.get_model("faults", "MaintenanceUpdate")

    for model in (MaintenanceRequest, MaintenanceUpdate):
        for old_value, new_value in CATEGORY_MAP.items():
            model.objects.filter(category=old_value).update(category=new_value)


def backwards(apps, schema_editor):
    """برگشت‌پذیر نیست؛ دسته‌های جدید در مدل قدیمی معادل دقیق ندارند."""


class Migration(migrations.Migration):

    dependencies = [
        ("faults", "0004_alter_maintenancerequest_status_and_more"),
        ("organizations", "0004_membership_role_room_active"),
        ("accounts", "0003_alter_user_role"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="maintenancerequest",
            name="category",
            field=models.CharField(
                choices=[
                    ("repairs", "تعمیرات"),
                    ("facilities", "تأسیسات"),
                    ("internet", "اینترنت"),
                    ("other", "متفرقه"),
                ],
                default="other",
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="maintenancerequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "ثبت‌شده"),
                    ("approved", "تأییدشده"),
                    ("in_progress", "در حال پیگیری"),
                    ("resolved", "انجام‌شده"),
                    ("rejected", "ردشده"),
                    ("irrelevant", "نامرتبط"),
                    ("cancelled", "لغو‌شده"),
                ],
                default="submitted",
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceupdate",
            name="category",
            field=models.CharField(
                choices=[
                    ("repairs", "تعمیرات"),
                    ("facilities", "تأسیسات"),
                    ("internet", "اینترنت"),
                    ("other", "متفرقه"),
                ],
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceupdate",
            name="status",
            field=models.CharField(
                choices=[
                    ("submitted", "ثبت‌شده"),
                    ("approved", "تأییدشده"),
                    ("in_progress", "در حال پیگیری"),
                    ("resolved", "انجام‌شده"),
                    ("rejected", "ردشده"),
                    ("irrelevant", "نامرتبط"),
                    ("cancelled", "لغو‌شده"),
                ],
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name="maintenancerequest",
            name="assigned_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_maintenance_requests",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="maintenancerequest",
            name="resolved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="MaintenanceRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("request", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="rating", to="faults.maintenancerequest")),
                ("reviewer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="maintenance_ratings", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "امتیاز درخواست",
                "verbose_name_plural": "امتیازهای درخواست",
            },
        ),
        migrations.RunPython(forwards, backwards),
    ]
