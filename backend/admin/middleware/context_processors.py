from django.http import HttpRequest

from admin.models import AdminPermission, AdminSessionModel


def permission_helper(request: HttpRequest):
    context = {}
    if request.path.startswith("/admin/") and hasattr(request, "_session"):
        sess: AdminSessionModel = request._session
        context["permission"] = {
            k.lower(): sess.has_permission(v)
            for k, v in AdminPermission._member_map_.items()
        }
    return context
