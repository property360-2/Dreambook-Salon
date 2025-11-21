from django.urls import path

from .views import (
    CustomerRegistrationView,
    DashboardView,
    EmailLoginView,
    EmailLogoutView,
    HomeView,
    UserManagementListView,
    UserCreateView,
    UserUpdateView,
    UserDetailView,
    UserDeactivateView,
    UserReactivateView,
    UserResetPasswordView,
    UserDeleteView,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("auth/login/", EmailLoginView.as_view(), name="login"),
    path("auth/logout/", EmailLogoutView.as_view(), name="logout"),
    path("auth/register/", CustomerRegistrationView.as_view(), name="register"),

    # User Management (Staff/Admin only)
    path("users/", UserManagementListView.as_view(), name="user_list"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/deactivate/", UserDeactivateView.as_view(), name="user_deactivate"),
    path("users/<int:pk>/reactivate/", UserReactivateView.as_view(), name="user_reactivate"),
    path("users/<int:pk>/reset-password/", UserResetPasswordView.as_view(), name="user_reset_password"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
]
