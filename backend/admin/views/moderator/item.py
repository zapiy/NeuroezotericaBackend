from django.shortcuts import render, redirect
from django.http import HttpRequest

from pyqumit import safe_get
from web import resolve_url, CustomJsonResponse
from admin.models import AdminUserModel, AdminPermission
from admin.middleware import admin_is_authenticated


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def moderator(request: HttpRequest, key: str):
    if key == "new":
        item = AdminUserModel()
    else:
        try:
            item = await AdminUserModel.objects.aget(key_name = key)
        except AdminUserModel.DoesNotExist:
            return redirect("admin:moderators")
        
        if request.method == "DELETE":
            await item.adelete()
            return CustomJsonResponse({
                "redirect": resolve_url("admin:moderators")
            })
        
    if request.method == "POST":
        item.key_name = safe_get(
            request.POST, "key_name", str, 
            prepare=lambda v: v.strip(), 
            validate=lambda v: len(v) in range(4, 121)
        )
        if item.key_name is None:
            return CustomJsonResponse({
                "modal": {
                    "content": "Длина ключа должна быть в диапазоне (4 - 50)"
                }
            })
            
        if item.key_name == "new":
            return CustomJsonResponse({
                "modal": {
                    "content": "Данный ключ не может быть задан!"
                }
            })
        
        if item.uuid is not None:
            await item.asave(force_update=True)
            return CustomJsonResponse({
                "redirect": resolve_url("admin:moderators"),
            })
        
        elif not (await AdminUserModel.objects.filter(key_name=item.key_name).aexists()):
            await item.asave(force_insert=True)
            return CustomJsonResponse({
                "redirect": resolve_url("admin:moderator", item.key_name),
                "modal": {
                    "title": "Успешно!",
                    "content": "Успешно добавлено!",
                }
            })
        
        return CustomJsonResponse({
            "modal": {
                "content": "Данный ключ уже существует!"
            }
        })

    return render(request, "admin/moderator/index.html", { "item": item })
