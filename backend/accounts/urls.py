from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    MeView,
    AdminCreateUserView,
    ChangePasswordView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view() , name="login"),
    path("register/", RegisterView.as_view() , name="register" ),
    path( "logout/", LogoutView.as_view(), name="logout" ),
    path( "me/", MeView.as_view(), name="me" ),
    path( "users/create/", AdminCreateUserView.as_view(), name="create-user" ),
    path( "change-password/", ChangePasswordView.as_view(), name="change-password" ),
]
