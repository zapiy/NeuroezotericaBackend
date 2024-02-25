from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsClient
from mobile_api.models import MobileUserModel, MobileClientServicePurchase
from mobile_api.serializers import FeedbackForm
from mobile_api.utils import ResponseType, typed_response


@api_view("POST")
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsClient])
async def chat_send_feedback(request: HttpRequest, uuid: str):
    user: MobileUserModel = request._user
    
    try:
        purchase = await MobileClientServicePurchase.objects.aget(
            uuid = uuid,
            status = MobileClientServicePurchase.Status.ARCHIVED,
            client = user.client_extra,
            service__telegram_link__isnull = True,
        )
    except MobileClientServicePurchase.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    form = FeedbackForm(data=request.DATA)
    
    if not form.is_valid():
        return typed_response(ResponseType.INVALID_FIELDS)
    
    purchase.status = purchase.Status.ARCHIVED_FEEDBACK
    purchase.rating = form.data['rating']
    purchase.feedback = form.data['feedback']
    await purchase.asave(update_fields=['status', 'rating', 'feedback'])
    
    return typed_response(ResponseType.OKAY)
