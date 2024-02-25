from django.shortcuts import render
from django.http import HttpRequest

from mobile_api.models import MobileExpertServiceCategory
from admin.models import AdminPermission
from ...middleware import admin_is_authenticated


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def categories_view(request: HttpRequest):
    return render(request, "admin/category/view.html", {
        "tab": "categories",
        "categories": MobileExpertServiceCategory.objects.all()
    })
    