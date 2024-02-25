from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse

from pyqumit import safe_get
from web import CustomJsonResponse
from middleware import allowed_methods
from ...middleware import admin_is_authenticated
from flutter_locale import *


@allowed_methods("POST")
@admin_is_authenticated()
async def translate_settings(request: HttpRequest, code: int):
    try:
        loc = APP_LOCALE.translation(code)
    except KeyError:
        return redirect("admin:translation")
    
    preview_name = safe_get(request.POST, "preview_name", str, validate=lambda v: len(v) in range(4, 101))
    if preview_name is None:
        return CustomJsonResponse({
            "modal": {
                "content": "Длина названия должна быть в диапазоне 4 - 100 символов."
            }
        })
    loc.preview_name = preview_name
    
    await APP_LOCALE.save()
    
    return CustomJsonResponse({
        "modal": {
            "title": "Успешно!",
            "content": "Успешно обновлено!",
        }
    })
