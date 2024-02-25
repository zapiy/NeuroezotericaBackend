from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.utils import ResponseType, typed_response


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def logout(request: HttpRequest):
    await request._session.adelete()
    return typed_response(ResponseType.OKAY)
