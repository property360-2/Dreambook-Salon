from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode
from django.core.exceptions import PermissionDenied


def role_required(*roles, login_url="core:login", redirect_field_name=REDIRECT_FIELD_NAME):
    """Ensure the user is authenticated and matches one of the required roles."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                params = urlencode({redirect_field_name: request.get_full_path()})
                return redirect(f"{reverse(login_url)}?{params}")
            if user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
