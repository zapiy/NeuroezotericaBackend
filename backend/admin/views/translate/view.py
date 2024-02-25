from django.shortcuts import render
from django.http import HttpRequest

from admin.middleware import admin_is_authenticated
from flutter_locale import APP_LOCALE


@admin_is_authenticated()
async def translate_view(request: HttpRequest):
    return render(request, "admin/translate/view.html", {
        "tab": "translate",
        "locales": APP_LOCALE.all_locales
    })
