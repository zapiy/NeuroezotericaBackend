from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsClient
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileClientServicePurchase


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsClient])
async def schedule_cancel(request: HttpRequest, uuid: str):
    user: MobileUserModel = request._user
    
    try:
        purchase = await MobileClientServicePurchase.objects.aget(
            status = MobileClientServicePurchase.Status.PRE_PAYMENT,
            uuid = uuid,
            client_id = user.uuid
        )
    except MobileClientServicePurchase.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    await purchase.adelete()
    
    return typed_response(ResponseType.OKAY, status=200)
