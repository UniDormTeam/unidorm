from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsSystemAdmin
from .serializers import (
    MeSerializer,
    AdminCreateUserSerializer,
    ChangePasswordSerializer,
    ManagerRegisterSerializer,
)


class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)

        user_data = MeSerializer(user).data

        return Response({
            "token": token.key,
            "user": user_data
        })



class RegisterView(APIView):
    """
    ثبت‌نام آزاد مدیر — نیازی به تأیید ادمین ندارد.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ManagerRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": MeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    """حذف توکن فعلی و خروج کاربر."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()

        return Response(
            {"detail": "خروج با موفقیت انجام شد."},
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """
    دریافت و ویرایش اطلاعات حساب کاربر فعلی.
    """

    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AdminCreateUserView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = AdminCreateUserSerializer
    permission_classes = [IsSystemAdmin]


class ChangePasswordView(APIView):
    """
    تغییر رمز عبور کاربر واردشده.

    کاملاً اختیاری است: کاربر هر وقت خواست رمزش را عوض می‌کند
    و هیچ اجباری در اولین ورود وجود ندارد.

        POST /api/auth/change-password/
        {"current_password": "4011111", "new_password": "..."}

    توکن ورود بعد از تغییر رمز معتبر می‌ماند؛ فرانت نیازی به
    ورود دوباره ندارد.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(
            {"detail": "رمز عبور با موفقیت تغییر کرد."},
            status=status.HTTP_200_OK,
        )
