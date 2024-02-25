from django.http import HttpRequest
from django.conf import settings
from django.db.models import Q
from datetime import datetime

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from web import CustomJsonResponse
from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsExpert
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import MobileUserModel, MobileExpertSchedule, MobileClientServicePurchase, MobileExpertScheduleFreetime


@api_view(["GET", "POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsExpert])
async def schedule_day(request: HttpRequest):
    user: MobileUserModel = request._user
    
    today = datetime.today().date()
    date = safe_get(
        request.GET, "date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
        validate=lambda v: v >= today
    )
    
    if date is None:
        return typed_response(ResponseType.INVALID_FIELDS)
    
    try:
        schedule = await MobileExpertSchedule.objects.aget(
            owner = user.expert_extra,
            date = date
        )
    except MobileExpertSchedule.DoesNotExist:
        schedule = None
    
    if request.method == "GET":    
        if schedule is None or schedule.status == schedule.Status.OUTLET:
            return CustomJsonResponse({
                "working": False
            })
        
        return CustomJsonResponse({
            "working": True,
            "work_range": (schedule.from_hour, schedule.to_hour),
            "free_times": [el.hour for el in schedule.freetimes.all()],
        })
        
    elif request.method == "POST":
        if (
            schedule is not None and (
                schedule.date == today
                or (
                    schedule is not None 
                    and (await schedule.purchases.filter(
                        Q(status = MobileClientServicePurchase.Status.PRE_PAYMENT)
                        | Q(status = MobileClientServicePurchase.Status.PAID),
                        service__telegram_link = None,
                    ).aexists())
                )
            )
        ):
            return typed_response(ResponseType.RESTRICT)
        
        working = safe_get(request.DATA, "working", bool)
        if working:
            work_range = safe_get(
                request.DATA, "work_range", list, 
                validate = lambda v: (
                    len(v) == 2
                    and all([isinstance(t, int) for t in v])
                    and v[1] > v[0]
                    and (v[1] - v[0]) > 2
                    and v[0] in range(0, 24)
                    and v[1] in range(0, 24)
                )
            )
            
            free_times = safe_get(
                request.DATA, "free_times", set,
                validate = lambda v: (
                    all([
                        (
                            isinstance(t, int) 
                            and t in range(work_range[0], work_range[1])
                        ) for t in v
                    ])
                )
            ) or []
        
        if (
            working is None
            or (working and work_range is None)
        ):
            return typed_response(ResponseType.INVALID_FIELDS)
        
        if schedule is None:
            schedule = MobileExpertSchedule(
                owner = user.expert_extra,
                date = date
            )
            await schedule.asave(force_insert=True)
        
        if not working:
            schedule.status = schedule.Status.OUTLET
            for ft in schedule.freetimes.all():
                await ft.adelete()
        else:
            schedule.status = schedule.Status.ON_SCHEDULE
            schedule.from_hour = work_range[0]
            schedule.to_hour = work_range[1]
            
            for ft in schedule.freetimes.all():
                if ft.hour not in free_times:
                    await ft.adelete()
                else:
                    free_times.remove(ft.hour)
                
            for ft in free_times:
                await MobileExpertScheduleFreetime(
                    date = schedule,
                    hour = ft
                ).asave(force_insert=True)

        await schedule.asave(force_update=True)

        return typed_response(ResponseType.OKAY)
