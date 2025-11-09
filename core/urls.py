from django.urls import path

from .views import (
    CustomerRegistrationView,
    DashboardView,
    EmailLoginView,
    EmailLogoutView,
    HomeView,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("auth/login/", EmailLoginView.as_view(), name="login"),
    path("auth/logout/", EmailLogoutView.as_view(), name="logout"),
    path("auth/register/", CustomerRegistrationView.as_view(), name="register"),
]
