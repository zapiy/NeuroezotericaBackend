from django.http import HttpRequest, HttpResponse
from django.db.models import Q

from middleware import allowed_methods
from web import CustomJsonResponse
from mobile_api.models import MobileUserModel
from admin.middleware import admin_is_authenticated


@allowed_methods("POST")
@admin_is_authenticated()
async def user_switch_block(request: HttpRequest, uuid: str):
    try:
        user: MobileUserModel = await MobileUserModel.objects.aget(
            Q(status = MobileUserModel.Status.ACTIVE) | Q(status = MobileUserModel.Status.BLOCKED),
            uuid = uuid,
        )
    except MobileUserModel.DoesNotExist:
        return CustomJsonResponse({
            "modal": {
                "content": "Данный пользователь больше не существует!"
            }
        })
        
    if user.status == MobileUserModel.Status.ACTIVE:
        user.status = MobileUserModel.Status.BLOCKED
        for sess in user.sessions.all():
            await sess.adelete()
    
    elif user.status == MobileUserModel.Status.BLOCKED:
        user.status = MobileUserModel.Status.ACTIVE
        
    await user.asave(force_update=True)
    return HttpResponse()
