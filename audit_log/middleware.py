from django.utils.deprecation import MiddlewareMixin

from .models import AuditLog


class AuditTrailMiddleware(MiddlewareMixin):
    """
    Lightweight audit middleware.
    Logs all authenticated non-read actions (POST/PUT/PATCH/DELETE) with path and status.
    """

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
    ACTION_MAP = {
        "POST": "CREATE",
        "PUT": "UPDATE",
        "PATCH": "UPDATE",
        "DELETE": "DELETE",
    }

    def process_response(self, request, response):
        try:
            self._log_request(request, response)
        except Exception:
            # Avoid breaking the request cycle if logging fails
            pass
        return response

    def _log_request(self, request, response):
        if request.method in self.SAFE_METHODS:
            return

        if getattr(request, "audit_log_skip", False):
            return

        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return

        path = request.path or ""
        if path.startswith("/static") or path.startswith("/media"):
            return

        action_type = self.ACTION_MAP.get(request.method, "UPDATE")
        resolver_match = getattr(request, "resolver_match", None)
        view_name = resolver_match.view_name if resolver_match else ""

        description = getattr(request, "audit_log_description", None)
        if not description:
            description = self._make_description(request.method, path, view_name, response.status_code)

        target_obj = getattr(request, "audit_log_target", None)
        metadata = {}

        if resolver_match and resolver_match.kwargs:
            metadata["route_kwargs"] = {k: AuditLog._stringify_value(v) for k, v in resolver_match.kwargs.items()}
        if request.GET:
            metadata["query_params"] = {k: AuditLog._stringify_value(v) for k, v in request.GET.items()}

        extra_metadata = getattr(request, "audit_log_metadata", None)
        if isinstance(extra_metadata, dict):
            metadata.update({k: AuditLog._stringify_value(v) for k, v in extra_metadata.items()})

        AuditLog.log_action(
            user=user,
            action_type=action_type,
            description=description,
            obj=target_obj,
            request=request,
            status_code=getattr(response, "status_code", None),
            source="MIDDLEWARE",
            metadata=metadata,
        )

    def _make_description(self, method, path, view_name, status_code):
        """Create a simple, non-technical description for the audit log."""
        verbs = {
            "POST": "Added",
            "PUT": "Updated",
            "PATCH": "Updated",
            "DELETE": "Removed",
        }
        verb = verbs.get(method, "Updated")

        resource = ""
        if view_name:
            resource = view_name.split(":")[0].replace("_", " ")
        if not resource and path:
            resource = path.strip("/").split("/")[0].replace("-", " ")

        resource = resource.title() if resource else "Item"

        return f"{verb} {resource} (status {status_code})"
