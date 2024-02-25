from django.http import HttpRequest
from django.db.models import DateField
from django.db.models.functions import Coalesce

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from mobile_api.serializers import ArchivedChatSerializer
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileUserModel, MobileClientServicePurchase


@api_view("GET")
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def archive_view(request: HttpRequest):
    user: MobileUserModel = request._user
    
    filters = {}
    if user.role == MobileUserModel.Role.CLIENT:
        filters["client"] = user.client_extra
        
    elif user.role == MobileUserModel.Role.EXPERT:
        filters["service__owner"] = user.expert_extra
    
    return CustomJsonResponse(ArchivedChatSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileClientServicePurchase.objects
                    .filter(
                        status = MobileClientServicePurchase.Status.ARCHIVED_FEEDBACK,
                        service__telegram_link__isnull = True,
                    )
                    .annotate(
                        schedule = Coalesce(
                            "date__date", "created_at",
                            output_field=DateField()
                        )
                    )
                    .order_by("-schedule")
            ),
            paginate=True
        )
    ).data)
