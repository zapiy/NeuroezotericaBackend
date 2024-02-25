from django.shortcuts import render, redirect
from django.http import HttpRequest

from pyqumit import safe_get
from web import resolve_url, CustomJsonResponse
from mobile_api.models import MobileExpertServiceCategory
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def category(request: HttpRequest, id: str):
    if id == "new":
        item = MobileExpertServiceCategory()
    else:
        try:
            item = await MobileExpertServiceCategory.objects.aget(id = id)
        except MobileExpertServiceCategory.DoesNotExist:
            return redirect("admin:categories")
        
        if request.method == "DELETE":
            await item.adelete()
            return CustomJsonResponse({
                "redirect": resolve_url("admin:categories")
            })
        
    if request.method == "POST":
        item.name = safe_get(
            request.POST, "name", str, 
            prepare=lambda v: v.strip(), 
            validate=lambda v: len(v) in range(4, 121)
        )
        if item.name is None:
            return CustomJsonResponse({
                "modal": {
                    "content": "Длина названия должна быть в диапазоне (4 - 120)",
                }
            })
        
        if item.uuid is not None:
            await item.asave(force_update=True)
        else:
            await item.asave(force_insert=True)
            return CustomJsonResponse({
                "redirect": resolve_url("admin:category", item.uuid),
                "modal": {
                    "title": "Успешно!",
                    "content": "Успешно добавлено!",
                }
            })
        
        return CustomJsonResponse({
            "modal": {
                "title": "Успешно!",
                "content": "Успешно обновлено!",
            }
        })

    return render(request, "admin/category/index.html", {
        "item": item
    })
