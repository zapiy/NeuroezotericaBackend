from django.http import HttpRequest
from django.conf import settings
from django.db.models import Q
from datetime import datetime

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from web import CustomJsonResponse
from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsClient
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileExpertSchedule, MobileClientServicePurchase


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsClient])
async def schedule_times(request: HttpRequest, uuid: str):
    today = datetime.today().date()
    date = safe_get(
        request.GET, "date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
        validate=lambda v: v >= today
    )
    
    if date is None:
        return typed_response(ResponseType.INVALID_FIELDS)
    
    try:
        schedule = await MobileExpertSchedule.objects.aget(
            owner_id = uuid,
            date = date,
            status = MobileExpertSchedule.Status.ON_SCHEDULE
        )
    except MobileExpertSchedule.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS, status = 404)
    
    filters = {}
    
    if date == today:
        start_hour = schedule.from_hour
        hour = datetime.now().hour + 1
        
        if hour > start_hour:
            start_hour = hour
        times = list(range(start_hour, schedule.to_hour))
        
        for t in schedule.freetimes.filter(hour__gt = hour).all():
            try: times.remove(t.hour)
            except ValueError: pass
            
        filters["hour__gt"] = hour
    else:
        times = list(range(schedule.from_hour, schedule.to_hour))
        for t in schedule.freetimes.all():
            try: times.remove(t.hour)
            except ValueError: pass
    
    for t in schedule.purchases.filter(
        Q(status = MobileClientServicePurchase.Status.PRE_PAYMENT)
        | Q(status = MobileClientServicePurchase.Status.PAID)
        | Q(status = MobileClientServicePurchase.Status.ACTIVE),
        service__telegram_link = None,
        **filters
    ).values_list("hour").all():
        try: times.remove(t[0])
        except ValueError: pass
    
    preview = safe_get(request.GET, "preview", bool, default=True)
    if preview:
        times = times[:6]
    return CustomJsonResponse(times)
