from django.shortcuts import render
from django.http import HttpRequest

from web import redirect, resolve_url, CustomJsonResponse
from pyqumit import safe_get
from ...middleware import admin_is_authenticated
from flutter_locale import *


@admin_is_authenticated()
async def translate_word(request: HttpRequest, code: str, text_code: str):
    try:
        loc = APP_LOCALE.translation(code)
    except KeyError:
        return redirect("admin:translation")
    
    if text_code not in APP_LOCALE.definions:
        return redirect("admin:translate", code, tab="translate")
    
    translate = loc.translate(text_code) or ""
    next_translate = next(loc.expected_translations.keys().__iter__(), None)
    
    if request.method == "POST":
        translate = safe_get(request.POST, "translate", str, validate=lambda v: len(v) >= 2)
        if translate is not None:
            try:
                loc.translate(text_code, translate)
                await APP_LOCALE.save()
                
                action = request.headers.get("x-action")
                if action == "next" and next_translate is not None:
                    return CustomJsonResponse({
                        "redirect": resolve_url("admin:translate_word", code, next_translate)
                    })
                return CustomJsonResponse({
                    "redirect": resolve_url("admin:translate", code)
                })
            
            except FlutterTranslateHasNoKeys as ex:
                return CustomJsonResponse({
                    "modal": {
                        "content": "Ошибка, не содержит ключей для вставки: \n" + ("\n".join([
                            f"- \"{k}\""
                            for k in ex.keys
                        ]))
                    }
                })
        return CustomJsonResponse({
            "modal": {
                "content": "Длина перевода должна составлять хотя-бы 2 символа!"
            }
        })
    
    return render(request, "admin/translate/translate_word.html", {
        "locale": {
            "code": code,
            "preview_name": loc.preview_name
        },
        "text": {
            "code": text_code,
            "base": APP_LOCALE.definions[text_code].translate,
            "value": translate,
            "has_next": (next_translate is not None),
        },
    })
