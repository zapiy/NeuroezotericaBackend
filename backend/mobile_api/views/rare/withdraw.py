from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileUserModel, MobileUserWithdrawHistory, MobileUserWithdrawHistory
from mobile_api.utils import ResponseType, typed_response
from mobile_api.serializers import WithdrawSerializer


@api_view(["GET", "POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def withdraw_view(request: HttpRequest):
    user: MobileUserModel = request._user
    
    if request.method == 'POST':
        if (
            user.balance < 10000
            or
            (await user.withdrawal.filter(
                status = MobileUserWithdrawHistory.Status.PROCESSING
            ).aexists())
        ):
            return typed_response(ResponseType.RESTRICT)
        
        form = WithdrawSerializer(data=request.DATA)
        if not form.is_valid():
            return typed_response(ResponseType.INVALID_FIELDS)

        await MobileUserWithdrawHistory.objects.acreate(
            **form.data,
            user = user,
        )
        
        return typed_response(ResponseType.OKAY)
    
    return CustomJsonResponse(WithdrawSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileUserWithdrawHistory.objects
                    .filter(user=user)
                    .order_by('-created_at')
            ),
            paginate=True,
            preview=True
        )
    ))
