from django.http import HttpRequest, HttpResponse

from web import CustomJsonResponse
from pyqumit import safe_get
from mobile_api.models import MobileUserModel
from admin.middleware import admin_is_authenticated


@admin_is_authenticated()
async def user_edit_data(request: HttpRequest, uuid: str):
    try:
        user: MobileUserModel = await MobileUserModel.objects.aget(
            uuid = uuid,
            status = MobileUserModel.Status.ACTIVE
        )
    except MobileUserModel.DoesNotExist:
        return CustomJsonResponse({
            "modal": {
                "content": "Данный пользователь больше не существует либо заблокирован!"
            }
        })
    
    user.first_name = safe_get(request.POST, "first_name", str, validate=lambda v: len(v) in range(4, 101))
    user.last_name = safe_get(request.POST, "last_name", str, allow_null=True, validate=lambda v: len(v) in range(4, 101))
    
    if user.first_name is None:
        return CustomJsonResponse({
            "modal": {
                "content": "Длина имени должна быть в диапазоне 4 - 100 символов"
            }
        })
        
    await user.expert_extra.asave(force_update=True)
    
    await user.asave(force_update=True)
    return HttpResponse()
