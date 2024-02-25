from django.http import HttpRequest
from django.conf import settings

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import process_image
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.utils import typed_response, ResponseType
from mobile_api.models import MobileUserModel


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def change_avatar(request: HttpRequest):
    user: MobileUserModel = request._user
    
    try:
        img = request.FILES["image"]
        if img.size > 5242880:
            return typed_response(ResponseType.INVALID_FIELDS)
        
        img_id = process_image(
            img.file,
            settings.BASE_DIR / f"media/avatar",
            max_dimention=400
        )
        user.avatar_uuid = img_id
        
        await user.asave(update_fields=['avatar_uuid'])
        return typed_response(ResponseType.OKAY)
    except:
        return typed_response(ResponseType.INVALID_FIELDS)
