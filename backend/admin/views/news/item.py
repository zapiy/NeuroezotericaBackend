from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.conf import settings

from pyqumit import safe_get
from web import CustomJsonResponse, resolve_url, process_image
from mobile_api.models import MobileNewsModel
from ...middleware import admin_is_authenticated


@admin_is_authenticated()
async def news_item(request: HttpRequest, uuid: str):
    if uuid == "new":
        item = MobileNewsModel()
    else:
        try:
            item = await MobileNewsModel.objects.aget(uuid = uuid)
        except MobileNewsModel.DoesNotExist:
            return redirect("admin:news")
        
        if request.method == "DELETE":
            await item.adelete()
            return HttpResponse()
        
    if request.method == "POST":
        item.title = safe_get(
            request.POST, "title", str, 
            prepare=lambda v: v.strip(), 
            validate=lambda v: len(v) in range(4, 121)
        )
        if item.title is None:
            return CustomJsonResponse({
                "modal": {
                    "content": "Длина заголовка должна быть в диапазоне (4 - 120)",
                }
            })
        
        item.content = safe_get(
            request.POST, "content", str, 
            prepare=lambda v: v.strip(), 
            validate=lambda v: len(v) in range(10, 1000)
        )
        if item.content is None:
            return CustomJsonResponse({
                "modal": {
                    "content": "Длина текста должна быть в диапазоне (10 - 1000)",
                }
            })
        
        if "wallpaper" in request.FILES:
            img = request.FILES["wallpaper"]
            if img.size > 5242880:
                return CustomJsonResponse({
                    "modal": {
                        "content": "Размер изображения не может превышать 5 МБ",
                    }
                })
            else:
                img_id = process_image(
                    img.file,
                    settings.BASE_DIR / f"media/news_wallpaper",
                    max_dimention=500
                )
                if img_id:
                    item.wallpaper_uuid = img_id
                else:
                    return CustomJsonResponse({
                        "modal": {
                            "content": "Данный формат изображений не поддерживается. (Доступно: .png, .jpg, .jpeg)",
                        }
                    })
        
        if item.uuid is not None:
            await item.asave(force_update=True)
        else:
            await item.asave(force_insert=True)
            
        return CustomJsonResponse({
            "redirect": resolve_url("admin:news"),
        })

    return render(request, "admin/news/index.html", { "item": item })
