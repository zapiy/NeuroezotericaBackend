from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileExpertServiceCategory
from mobile_api.serializers import ServiceCategorySerializer


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def services_category_view(request: HttpRequest):
    return CustomJsonResponse(ServiceCategorySerializer(
        instance=MobileExpertServiceCategory.objects.all(), many=True).data)
