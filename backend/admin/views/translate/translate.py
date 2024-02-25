from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.db.models import Q

from pyqumit import safe_get
from web import CustomJsonResponse, resolve_url
from ...middleware import admin_is_authenticated
from flutter_locale import *


ALL_TABS = {
    "translate": "Таблица перевода",
    "settings": "Управление",
}


@admin_is_authenticated()
async def translate(request: HttpRequest, code: str):
    if request.method == "DELETE":
        try:
            APP_LOCALE.rem_translation(code)
            await APP_LOCALE.save()
        except: pass
        return CustomJsonResponse({
            "redirect": resolve_url("admin:translation")
        })
    
    if code == "add":
        return render(request, "admin/translate/add_locale.html", {
            "locales": sorted(APP_LOCALE.needed_locales)
        })
        
    try:
        loc = APP_LOCALE.translation(code)
    except KeyError:
        return redirect("admin:translation")
    
    current_tab = safe_get(
        request.GET, "tab", str, 
        default="translate",
        validate=lambda v: v in ALL_TABS
    )
    
    context = {
        "locale": {
            "code": code,
            "preview_name": loc.preview_name or ""
        },
        "tabs": {
            "all": ALL_TABS,
            "current": current_tab,
        }
    }
    
    if current_tab == "settings":
        return render(request, "admin/translate/settings.html", context)
    
    context.update({
        "table": {
            "complete": loc.completed_translations,
            "expected": loc.expected_translations,
        }
    })
    return render(request, "admin/translate/translate_table.html", context)
    