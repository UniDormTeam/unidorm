import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    نقش عضو در سازمان (دانشجو/تأسیسات/اینترنت) و شماره اتاق اضافه می‌شود.
    محدودیت قبلی «فقط دانشجو» از فیلد user برداشته می‌شود.
    """

    dependencies = [
        ("organizations", "0003_alter_organizationmembership_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="organizationmembership",
            name="role",
            field=models.CharField(
                choices=[
                    ("student", "دانشجو"),
                    ("facilities", "مسئول تأسیسات"),
                    ("internet", "مسئول اینترنت"),
                ],
                default="student",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="room_number",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="organizationmembership",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organization_memberships",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
