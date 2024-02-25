from django.http import HttpRequest

from web import CustomJsonResponse, resolve_url
from middleware import allowed_methods
from mobile_api.models import MobileUserModel, MobileUserWithdrawHistory
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission


@allowed_methods("POST", "DELETE")
@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def user_withdrawal(request: HttpRequest, uuid: str):
    try: 
        user: MobileUserModel = await MobileUserModel.objects.aget(
            uuid = uuid,
            status = MobileUserModel.Status.ACTIVE
        )
    except MobileUserModel.DoesNotExist:
        return CustomJsonResponse({
            "redirect": resolve_url("admin:users")
        })
    
    withdraw = await MobileUserWithdrawHistory.objects.filter(
        user = user,
        status = MobileUserWithdrawHistory.Status.PROCESSING
    ).afirst()
    if withdraw is None:
        return CustomJsonResponse({
            "redirect": resolve_url("admin:user", user.uuid, tab="withdraw_history")
        })
        
    if request.method == "DELETE":
        withdraw.status = MobileUserWithdrawHistory.Status.FAIL
        await withdraw.asave(force_update=True)
        
        return CustomJsonResponse({
            "redirect": resolve_url("admin:user", user.uuid, tab="withdraw_history"),
            "modal": {
                "title": "Успешно!",
                "content": "Запрос на выплату успешно отклонен!"
            }
        })

    if user.role == MobileUserModel.Role.CLIENT:
        withdraw.count = user.balance
        user.balance = 0
        await user.asave(force_update=True)

    elif user.role == MobileUserModel.Role.EXPERT:
        balance = user.balance
        comission = user.expert_extra.service_commission or 5
        
        withdraw.service_profit = (balance * (comission / 100))
        withdraw.count = balance - withdraw.service_profit
        
        user.balance = 0
        await user.asave(force_update=True)
    
    withdraw.status = MobileUserWithdrawHistory.Status.DONE
    await withdraw.asave(force_update=True)

    return CustomJsonResponse({
        "redirect": resolve_url("admin:user", user.uuid, tab="withdraw_history"),
        "modal": {
            "title": "Успешно!",
            "content": "Деньги успешно выведены, баланс пользователя обнулен!"
        }
    })
