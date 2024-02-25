from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsExpert
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileClientServicePurchase


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsExpert])
async def schedule_sessions_cancel(request: HttpRequest, uuid: str):
    user: MobileUserModel = request._user
    
    try:
        session = await MobileClientServicePurchase.objects.aget(
            uuid=uuid,
            date__owner = user.expert_extra,
            status = MobileClientServicePurchase.Status.PAID,
            service__telegram_link = None
        )
    except MobileClientServicePurchase.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    session.status = session.Status.CANCELLED
    await session.asave(update_fields=['status'])
    
    session.client.user.balance += session.price
    await session.client.user.asave(update_fields=['balance'])
    
    return typed_response(ResponseType.OKAY)
    