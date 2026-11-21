from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminCreateUserView,
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    UserListView,
)

app_name = "accounts"

urlpatterns = [
    # ورود و ثبت‌نام مدیر (هر دو مسیر ثبت‌نام برای سازگاری نگه داشته شده‌اند)
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("register/manager/", RegisterView.as_view(), name="register-manager"),
    
    # تمدید access token با refresh token
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # خروج (بلک‌لیست کردن refresh token)
    path("logout/", LogoutView.as_view(), name="logout"),

    # پروفایل کاربر جاری
    path("me/", MeView.as_view(), name="me"),

    path("change-password/", ChangePasswordView.as_view(), name="change-password"),

    # مدیریت کاربران توسط ادمین کل
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/create/", AdminCreateUserView.as_view(), name="create-user"),
]
