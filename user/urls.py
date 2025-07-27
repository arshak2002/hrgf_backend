from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from user.views import CustomTokenObtainPairView, RegisterUserView, UserChangePasswordView, UserView


router = routers.DefaultRouter()

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"register/", RegisterUserView.as_view(), name="register"),
    path(r"login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "me/change-password/",
        UserChangePasswordView.as_view(),
        name="change-password",
    ),
    path("me/", UserView.as_view(), name="user-me"),
    path(
        r"login/",
        CustomTokenObtainPairView.as_view(),
        name="custom_token_obtain_pair",
    ),
]
