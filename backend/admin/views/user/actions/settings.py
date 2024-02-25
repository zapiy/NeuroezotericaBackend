from django.http import HttpRequest, HttpResponse

from pyqumit import safe_get
from web import CustomJsonResponse
from middleware import allowed_methods
from mobile_api.models import MobileUserModel
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission


@allowed_methods("POST")
@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def user_settings(request: HttpRequest, uuid: str):
    try: 
        user: MobileUserModel = await MobileUserModel.objects.aget(uuid=uuid)
    except MobileUserModel.DoesNotExist:
        return HttpResponse()
    
    if user.role == MobileUserModel.Role.EXPERT:
        comission = safe_get(request.POST, "comission", int, validate=lambda v: v in range(1, 101))
        if comission is None:
            return CustomJsonResponse({
                "modal": {
                    "content": "Комиссия может быть только в диапазоне 1 - 100"
                }
            })
            
        user.expert_extra.service_commission = comission
        await user.expert_extra.asave(force_update=True)
    
    return CustomJsonResponse({
        "modal": {
            "title": "Успешно!",
            "content": "Успешно сохранено!"
        }
    })
