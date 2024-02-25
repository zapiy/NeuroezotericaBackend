from django.http import HttpRequest

from adrf.decorators import api_view
from flutter_locale import APP_LOCALE
from web import CustomJsonResponse


@api_view(["GET"])
async def locales(request: HttpRequest):
    return CustomJsonResponse([
        {
            "code": loc.code,
            "preview_name": loc.preview_name
        }
        for loc in APP_LOCALE.all_locales
        if loc.available
    ])
