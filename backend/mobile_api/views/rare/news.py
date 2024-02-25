from django.http import HttpRequest
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileNewsModel
from mobile_api.serializers import NewsSerializer


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def news_view(request: HttpRequest):
    return CustomJsonResponse(NewsSerializer(
        many=True,
        instance=await wrap_filters(
            request, (
                MobileNewsModel.objects
                    .order_by("-created_at")
            ),
            paginate=True,
            preview=True
        )
    ).data)
