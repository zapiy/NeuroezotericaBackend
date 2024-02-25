from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsClient
from mobile_api.models import MobileClientReferalRelation, MobileUserModel
from mobile_api.serializers import ReferalUserInfoSerializer


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsClient])
async def referals_view(request: HttpRequest):
    user: MobileUserModel = request._user
    
    return CustomJsonResponse(ReferalUserInfoSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileClientReferalRelation.objects
                    .filter(by = user.client_extra)
                    .order_by("-created_at")
            ),
            paginate=True,
            preview=True,
            queryable=[
                "user__user__first_name",
                "user__user__last_name",
                "user__user__phone"
            ]
        )
    ).data)
