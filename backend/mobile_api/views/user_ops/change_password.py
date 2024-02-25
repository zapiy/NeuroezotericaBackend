from django.http import HttpRequest
from django.contrib.auth.hashers import make_password, check_password

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.utils import typed_response, ResponseType
from mobile_api.models import MobileUserModel


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def change_password(request: HttpRequest):
    user: MobileUserModel = request._user
    
    current: str = safe_get(request.DATA, "current", str, validate=lambda v: len(v) in range(7, 26))
    password: str = safe_get(request.DATA, "password", str, validate=lambda v: len(v) in range(7, 26))
    print(current, password)
    if (
        current is None or password is None
        or not check_password(current, user.password_hash)
    ):
        return typed_response(ResponseType.INVALID_FIELDS, status=409)
    
    user.password_hash = make_password(password)
    await user.asave(force_update=True)
    
    return typed_response(ResponseType.OKAY)
