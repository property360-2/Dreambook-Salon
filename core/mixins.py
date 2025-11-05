"""
Role-based access control mixins for class-based views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .models import User


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin to restrict CBV access to specific user roles.

    Usage:
        class MyView(RoleRequiredMixin, TemplateView):
            allowed_roles = [User.Roles.ADMIN]
            ...
    """

    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if self.allowed_roles and request.user.role not in self.allowed_roles:
            raise PermissionDenied(
                f"You need {' or '.join(self.allowed_roles)} role to access this page."
            )

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for admin-only views."""

    allowed_roles = [User.Roles.ADMIN]


class StaffOrAdminRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for staff or admin views."""

    allowed_roles = [User.Roles.ADMIN, User.Roles.STAFF]


class CustomerRequiredMixin(RoleRequiredMixin):
    """Shortcut mixin for customer-only views."""

    allowed_roles = [User.Roles.CUSTOMER]
