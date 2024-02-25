from django.http import HttpRequest
from django.db.models import Q

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsExpert
from mobile_api.events import AppActions
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileClientServicePurchase, MobileServicePurchaseMessage


@api_view("POST")
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsExpert])
async def chat_finish(request: HttpRequest, uuid: str):
    user: MobileUserModel = request._user
    
    try:
        purchase = await MobileClientServicePurchase.objects.aget(
            Q(status = MobileClientServicePurchase.Status.ACTIVE),
            uuid = uuid,
            service__owner = user.expert_extra,
            service__telegram_link__isnull= True,
        )
    except MobileClientServicePurchase.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    purchase.status = MobileClientServicePurchase.Status.ARCHIVED
    await purchase.asave(update_fields=['status'])
    
    user.balance += purchase.real_price
    await user.asave(update_fields=['balance'])
    
    await AppActions.send_message(user, purchase, MobileServicePurchaseMessage.Type.ENDED)
    AppActions.on_chat_state_changed(purchase)
    
    return typed_response(ResponseType.OKAY, status=200)
