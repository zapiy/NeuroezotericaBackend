from django.http import HttpRequest
from django.conf import settings

from adrf.decorators import api_view

from web import CustomJsonResponse
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel


@api_view(["GET"])
async def inviting_preview(request: HttpRequest, code: str):
    if len(code) != 8:
        return typed_response(ResponseType.INVALID_FIELDS)
    
    try:
        user = await MobileUserModel.objects.aget(client_extra__referal_code = code)
    except MobileUserModel.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    return CustomJsonResponse({
        "uuid": user.uuid,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": settings.INTERNET_URL + (
            f"/media/avatar/{user.avatar_uuid}.jpg"
            if user.avatar_uuid else
            "/static/media_defaults/avatar.jpg"
        )
    })
