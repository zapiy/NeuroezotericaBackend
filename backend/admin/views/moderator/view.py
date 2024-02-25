from django.shortcuts import render
from django.http import HttpRequest

from admin.models import AdminUserModel, AdminPermission
from admin.middleware import admin_is_authenticated


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def moderators_view(request: HttpRequest):
    return render(request, "admin/moderator/view.html", {
        "tab": "moderators",
        "moderators": AdminUserModel.objects.all()
    })
    