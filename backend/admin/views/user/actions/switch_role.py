from django.http import HttpRequest, HttpResponse

from middleware import allowed_methods
from mobile_api.models import MobileUserModel, MobileUserExpertExtra
from admin.middleware import admin_is_authenticated


@allowed_methods("POST")
@admin_is_authenticated()
async def user_switch_role(request: HttpRequest, uuid: str):
    try: 
        user: MobileUserModel = await MobileUserModel.objects.aget(
            uuid = uuid,
            status = MobileUserModel.Status.ACTIVE,
        )
        
        if user.role == MobileUserModel.Role.CLIENT:
            user.role = MobileUserModel.Role.EXPERT
            if not hasattr(user, 'expert_extra') or user.expert_extra is None:
                await MobileUserExpertExtra(
                    user = user
                ).asave(force_insert=True)
                
        elif user.role == MobileUserModel.Role.EXPERT:
            user.role = MobileUserModel.Role.CLIENT
        
        user.selected_role = user.role
            
        await user.asave(force_update=True)
    except MobileUserModel.DoesNotExist:
        pass
    return HttpResponse()
