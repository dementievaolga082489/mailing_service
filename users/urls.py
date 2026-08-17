from django.urls import path
from .views import (
    UserLoginView,
    UserRegistrationView,
    user_logout_view,
    UserProfileView,
    verify_email,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    UserListView,
    UserBlockView,
)

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("logout/", user_logout_view, name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("email-confirm/<str:token>/", verify_email, name="verify_email"),
    # Восстановление пароля (простой способ)
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/<str:token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/block/", UserBlockView.as_view(), name="user_block"),
]
