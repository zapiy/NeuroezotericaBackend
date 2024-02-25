from django.http import HttpRequest

from adrf.decorators import api_view
from flutter_locale import APP_LOCALE
from web import CustomJsonResponse


@api_view(["GET"])
async def locale(request: HttpRequest, code: str):
    loc = APP_LOCALE.translation(code, safe=True)
    if loc is None:
        loc = APP_LOCALE.translation(APP_LOCALE.default_code, safe=True)
    
    return CustomJsonResponse({
        "_preview": loc.preview_name,
        **APP_LOCALE._translations[APP_LOCALE.default_code]._translations,
        **loc._translations,
    })
