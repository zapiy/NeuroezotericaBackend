from django.http import HttpRequest
from datetime import datetime

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsExpert
from mobile_api.events import AppActions
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileClientServicePurchase, MobileServicePurchaseMessage


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsExpert])
async def chat_start(request: HttpRequest, uuid: str):
    user: MobileUserModel = request._user
    
    try:
        purchase = await MobileClientServicePurchase.objects.aget(
            status = MobileClientServicePurchase.Status.PAID,
            uuid = uuid,
            service__owner = user.expert_extra,
            service__telegram_link__isnull= True,
        )
    except MobileClientServicePurchase.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    now = datetime.today()
    today = now.date()
    hour = now.hour
    
    if (
        today < purchase.date.date
        or (purchase.date.date == today and hour < purchase.hour)
    ):
        return typed_response(ResponseType.RESTRICT)
    
    purchase.status = MobileClientServicePurchase.Status.ACTIVE
    await purchase.asave(update_fields=['status'])
    
    await AppActions.send_message(user, purchase, MobileServicePurchaseMessage.Type.STARTED)
    AppActions.on_chat_state_changed(purchase)
    
    return typed_response(ResponseType.OKAY)
