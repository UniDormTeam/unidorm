from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # احراز هویت: login / register / refresh / logout / me
    path("api/auth/", include("accounts.urls")),
    # سازمان‌ها، اعضا و مدیران
    path("api/", include("organizations.urls")),
    # اعلام خرابی‌ها (مسیرهای شخصی و مسیرهای داخل سازمان)
    path("api/", include("faults.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
