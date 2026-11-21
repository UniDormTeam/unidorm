"""ویوهای احراز هویت با JWT (access + refresh)."""

from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsSystemAdmin
from .serializers import (
    AdminCreateUserSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    ManagerRegisterSerializer,
    MeSerializer,
)
from .utils import build_login_payload


def issue_tokens(user):
    """ساخت جفت توکن JWT برای کاربر."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class LoginView(APIView):
    """
    POST /api/auth/login/

    ورودی: username, password
    خروجی: توکن‌ها + اطلاعات کاربر + سازمان‌ها + توانایی‌ها
    فرانت‌اند با role و organizations کاربر را به داشبورد درست می‌فرستد.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "نام کاربری یا رمز عبور اشتباه است."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "این حساب کاربری غیرفعال شده است."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "tokens": issue_tokens(user),
                **build_login_payload(user),
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    """
    POST /api/auth/register/  (و /api/auth/register/manager/)

    ثبت‌نام مدیر. بعد از ساخت حساب، همان اطلاعات ورود برگردانده می‌شود
    تا فرانت‌اند بلافاصله کاربر را وارد کند.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ManagerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "ثبت‌نام مدیر با موفقیت انجام شد.",
                "tokens": issue_tokens(user),
                **build_login_payload(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    refresh token را در لیست سیاه قرار می‌دهد تا دیگر قابل استفاده نباشد.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "ارسال refresh token الزامی است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response(
                {"detail": "توکن نامعتبر یا منقضی شده است."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "خروج از حساب کاربری با موفقیت انجام شد."},
            status=status.HTTP_205_RESET_CONTENT,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /api/auth/me/ — مشاهده و ویرایش اطلاعات کاربر جاری."""

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — تغییر رمز توسط خود کاربر."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])

        return Response(
            {"message": "رمز عبور با موفقیت تغییر کرد."},
            status=status.HTTP_200_OK,
        )


class AdminCreateUserView(generics.CreateAPIView):
    """
    POST /api/auth/users/create/

    ساخت حساب توسط ادمین کل. مدیر سازمان هم می‌تواند از مسیر اعضای
    سازمان حساب بسازد؛ این مسیر برای ساخت مدیر/دانشجوی مستقل است.
    """

    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "role_display": user.get_role_display(),
            },
            status=status.HTTP_201_CREATED,
        )


class UserListView(generics.ListAPIView):
    """
    GET /api/auth/users/?role=student

    فهرست کاربران برای ادمین کل؛ برای انتخاب مدیر یا مسئولین در پنل
    مدیریتی کاربرد دارد.
    """

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by("username")
        role = self.request.query_params.get("role")

        if role:
            queryset = queryset.filter(role=role)

        return queryset
