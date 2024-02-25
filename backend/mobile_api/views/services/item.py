from datetime import datetime
from django.http import HttpRequest

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from web import CustomJsonResponse
from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsExpert
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileExpertService, MobileExpertServiceCategory
from mobile_api.serializers import ServiceInfoForm


ARCHIVED_DATE_FORMAT = "%d.%m.%Y"


@api_view(["GET", "POST", "PUT", "DELETE"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsExpert])
async def service_item(request: HttpRequest):
    user: MobileUserModel = request._user
    
    if request.method == "PUT":
        service = MobileExpertService(
            owner = user.expert_extra
        )
    else:
        uuid = safe_get(
            (request.GET if request.method == "GET" else request.DATA), 
            "uuid", int, validate=lambda v: v > 0
        )
        
        if uuid is None:
            return typed_response(ResponseType.INVALID_FIELDS)
        
        try:
            service = await MobileExpertService.objects.aget(
                uuid = uuid,
                owner = user.expert_extra,
                status = MobileExpertService.Status.ALIVE
            )
        except MobileExpertService.DoesNotExist:
            return typed_response(ResponseType.INVALID_FIELDS, status=404)
    
    if request.method == "GET":
        return CustomJsonResponse(ServiceInfoForm(instance=service).data)
        
    elif request.method == "DELETE":
        dt = datetime.now().strftime(ARCHIVED_DATE_FORMAT)
        service.name += f" ({dt})"
        service.status = MobileExpertService.Status.ARCHIVE
        await service.asave(update_fields=['name', 'status'])
        return typed_response(ResponseType.OKAY)
    
    form = ServiceInfoForm(instance=service, data=request.DATA)
    if not form.is_valid():
        return typed_response(ResponseType.INVALID_FIELDS)
    
    old_link = service.telegram_link
    form.save()
    
    if request.method == "POST":
        if (
            (old_link is None and service.telegram_link is not None)
            or
            (old_link is not None and service.telegram_link is None)
        ):
            return typed_response(ResponseType.INVALID_FIELDS)
    
    if (
        service.telegram_link is not None 
        and not service.telegram_link.startswith("https://t.me/")
    ):
        return typed_response(ResponseType.INVALID_FIELDS)
    
    category_uuid = safe_get(request.DATA, "category", int, validate=lambda v: v > 0)
    if category_uuid is not None:
        try:
            category = (await MobileExpertServiceCategory.objects.values_list("id").aget(
                uuid = category_uuid
            ))[0]
        except MobileExpertServiceCategory.DoesNotExist:
            category = None
    
    if (
        request.method == "PUT" and
        (category_uuid is None or category is None)
    ):
        return typed_response(ResponseType.INVALID_FIELDS)
    
    service.category_id = category
    
    if request.method == "POST":
        await service.asave(force_update=True)
    if request.method == "PUT":
        await service.asave(force_insert=True)
    
    return typed_response(ResponseType.OKAY)
