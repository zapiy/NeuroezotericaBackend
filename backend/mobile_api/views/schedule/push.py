from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.db.models import Q
from datetime import datetime
import logging

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from mobile_api.authentication import MobileAuthentication, IsAuthenticatedAsClient
from mobile_api.utils import ResponseType, typed_response
from mobile_api.models import (
    MobileUserModel, MobileExpertSchedule, MobileClientServicePurchase, 
    MobileExpertService
)
from mobile_api.third_party import ProdamusAPI

logger = logging.getLogger("schedule_push")
logger.setLevel(logging.DEBUG)


@api_view(["POST"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticatedAsClient])
async def schedule_push(request: HttpRequest):
    user: MobileUserModel = request._user
    
    if await user.client_extra.purchases.filter(
        status = MobileClientServicePurchase.Status.PRE_PAYMENT
    ).aexists():
        return typed_response(ResponseType.RESTRICT)
    
    service_uuid = safe_get(request.DATA, "service", str, validate=lambda v: v > 0)
    
    try:
        service = await MobileExpertService.objects.aget(
            uuid = service_uuid,
            owner__user__status = MobileUserModel.Status.ACTIVE,
            status = MobileExpertService.Status.ALIVE
        )
    except MobileExpertService.DoesNotExist:
        return typed_response(ResponseType.INVALID_FIELDS)

    schedule, hour = None, None
    
    if service.telegram_link is None:
        today = datetime.today().date()
    
        date = safe_get(
            request.DATA, "date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
            validate=lambda v: v >= today
        )
        
        hour = safe_get(request.DATA, "hour", int, validate=lambda v: v in range(0, 24))
        
        if (
            date is None
            or hour is None
        ):
            return typed_response(ResponseType.INVALID_FIELDS)
        
        try:
            schedule = await MobileExpertSchedule.objects.aget(
                owner = service.owner,
                date = date,
                status = MobileExpertSchedule.Status.ON_SCHEDULE
            )
            
            if (
                (date == today and hour not in range(datetime.now().hour + 1, schedule.to_hour))
                or hour not in range(schedule.from_hour, schedule.to_hour)
                or (await schedule.freetimes.filter(hour = hour).aexists())
                or (await schedule.purchases.filter(
                    Q(status = MobileClientServicePurchase.Status.PRE_PAYMENT)
                    | Q(status = MobileClientServicePurchase.Status.PAID)
                    | Q(status = MobileClientServicePurchase.Status.ACTIVE),
                    hour = hour,
                    service__telegram_link__isnull = True
                ).aexists())
            ):
                return typed_response(ResponseType.UNKNOWN_OPERATION)
            
        except MobileExpertSchedule.DoesNotExist:
            return typed_response(ResponseType.INVALID_FIELDS)
    
    price = service.price
    need_pay = True
    
    discount = safe_get(request.DATA, "discount", int, validate=lambda v: v in range(1, 2001))
    
    if discount is not None and (
        discount <= user.client_extra.bonuses
    ):
        if discount < price:
            price -= discount
            user.client_extra.bonuses -= discount
        elif discount >= price:
            user.client_extra.bonuses -= price
            price = 0
            need_pay = False
        
    purchase = MobileClientServicePurchase(
        client = user.client_extra,
        status = (
            MobileClientServicePurchase.Status.PRE_PAYMENT
            if need_pay else
            MobileClientServicePurchase.Status.PAID
        ),
        service = service,
        date = schedule,
        hour = hour,
        real_price = service.price,
        price = price,
    )
    
    if not await ProdamusAPI.create_link(purchase):
        logger.info(f"Fail create prodamus payment link [{user.uuid}] of '{service.name}'[{service.uuid}]")
        return HttpResponse("3Party error", status = 500)
    
    logger.info(f"Create purchase [{user.uuid}] of '{service.name}'[{service.uuid}] = {service.price}, Need pay?: {need_pay}, Confirm Hash: {purchase.confirm_hash}")

    await purchase.asave(force_insert=True)
    await user.client_extra.asave(force_update=True)
    
    return typed_response(ResponseType.OKAY, data={ "link": purchase.payment_link })
