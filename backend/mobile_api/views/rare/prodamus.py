from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse

from ...models import MobileClientServicePurchase


async def prodamus_confirm(request: HttpRequest, uuid: int):
    try:
        purchase = await MobileClientServicePurchase.objects.aget(
            status = MobileClientServicePurchase.Status.PRE_PAYMENT,
            confirm_hash = uuid
        )
    except (ValidationError, MobileClientServicePurchase.DoesNotExist):
        return HttpResponse("Invalid hash", status = 403)
    
    purchase.status = MobileClientServicePurchase.Status.PAID
    await purchase.asave(force_update=True)
    
    client = purchase.client
    client.bonuses += purchase.price * 0.05
    await client.asave(force_update=True)
    
    if hasattr(client, "referred_by") and client.referred_by is not None:
        count_referals = client.referred_by.by.invitations.count()
        bonuses = 0
        
        if count_referals <= 0:
            bonuses = 0
        if count_referals in range(1, 51):
            bonuses = purchase.price * 0.02
        elif count_referals in range(51, 101):
            bonuses = purchase.price * 0.025
        elif count_referals in range(101, 201):
            bonuses = purchase.price * 0.03
        elif count_referals in range(201, 301):
            bonuses = purchase.price * 0.035
        elif count_referals in range(301, 401):
            bonuses = purchase.price * 0.04
        elif count_referals in range(401, 501):
            bonuses = purchase.price * 0.045
        elif count_referals > 500:
            bonuses = purchase.price * 0.05
            
        client.referred_by.by.user.balance += bonuses
        client.referred_by.points += bonuses
        await client.referred_by.asave(force_update=True)
        await client.referred_by.by.user.asave(force_update=True)
    
    if purchase.service.telegram_link != None:
        owner = purchase.service.owner
        owner.user.balance += purchase.real_price
        await owner.user.asave(force_update=True)
    
    return HttpResponse("Okay", status = 200)
