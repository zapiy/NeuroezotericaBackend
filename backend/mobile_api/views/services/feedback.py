from django.http import HttpRequest, HttpResponse
from django.db.models import DateField
from django.db.models.functions import Coalesce

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileExpertService, MobileClientServicePurchase, MobileExpertServiceCategory
from mobile_api.serializers import ArchivedChatSerializer


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def service_feedback_view(request: HttpRequest, uuid: str):
    try:
        service = (await MobileExpertService.objects.values_list("id").aget(
            uuid = uuid,
            status = MobileExpertService.Status.ALIVE
        ))[0]
    except (KeyError, ValueError, MobileExpertServiceCategory.DoesNotExist):
        return HttpResponse("Not Found", status = 404)
    
    return CustomJsonResponse(ArchivedChatSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileClientServicePurchase.objects
                    .filter(
                        service = service,
                        status = MobileClientServicePurchase.Status.ARCHIVED_FEEDBACK
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
