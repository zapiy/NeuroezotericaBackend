import logging
from django.http import HttpRequest
from django.db.models import Sum

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileUserModel, MobileUserWithdrawHistory
from mobile_api.utils import ResponseType, typed_response
from mobile_api.serializers import ExpertInfoSerializer, ClientInfoSerializer

logger = logging.getLogger("mobile_user_info")
logger.setLevel(logging.DEBUG)


@api_view(["GET", "POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def user_info(request: HttpRequest):
    user: MobileUserModel = request._user
    
    form = None
    if request.method == "POST" and request.DATA:
        data: dict = request.DATA
        logger.info(f"+{user.phone} request change info: {data}")
        
        if user.selected_role == user.Role.EXPERT:
            form = ExpertInfoSerializer(user, data)
        elif user.selected_role == user.Role.CLIENT:
            form = ClientInfoSerializer(user, data)

        if not form.is_valid():
            return typed_response(ResponseType.INVALID_FIELDS)

        form.save()
        
        await user.asave(force_update=True)
        if user.selected_role == user.Role.EXPERT:
            await user.expert_extra.asave(force_update=True)
    
    if form is None:
        if user.selected_role == user.Role.EXPERT:
            form = ExpertInfoSerializer(instance=user)
        elif user.selected_role == user.Role.CLIENT:
            form = ClientInfoSerializer(instance=user)
    
    data = form.data
    
    data['total_withdraw'] = (
        MobileUserWithdrawHistory.objects.filter(
            user = user,
            status = MobileUserWithdrawHistory.Status.DONE
        ).values_list(Sum('count'))[0]
    ) or 0
    
    if user.selected_role == user.Role.CLIENT:
        data["referals_count"] = user.client_extra.invitations.count()
    
    return CustomJsonResponse(data)
