from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.db.models import Q, Sum

from pyqumit import safe_get
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission, AdminSessionModel
from mobile_api.models import (
    MobileUserModel, MobileClientServicePurchase, MobileUserWithdrawHistory,
    MobileExpertService
)

BASE_TABS = [
    ("sessions", "Сессии"),
    ("edit_data", "Редактирование"),
    ("settings", "Управление"),
]


@admin_is_authenticated()
async def user_item(request: HttpRequest, uuid: str):
    try:
        user = await MobileUserModel.objects.aget(uuid = uuid)
    except MobileUserModel.DoesNotExist:
        return redirect("admin:users")
    
    if user.status != MobileUserModel.Status.ACTIVE:
        return render(request, "admin/user/base.html", {
            "user": user,
        })
    
    session: AdminSessionModel = request._session
    
    if user.role == MobileUserModel.Role.CLIENT:
        user.referals_count = user.client_extra.invitations.count()
    
    tabs = BASE_TABS.copy()
    notifications = []
    
    if session.has_permission(AdminPermission.OWNER):
        tabs.insert(2, ("withdraw_history", "Последние выводы"))
    
    active_withdraw = await MobileUserWithdrawHistory.objects.filter(
        user = user,
        status = MobileUserWithdrawHistory.Status.PROCESSING
    ).afirst()
    if active_withdraw is not None:
        notifications.append("Ожидает вывода средств")
        if session.has_permission(AdminPermission.OWNER):
            tabs.insert(2, ("withdraw", "Вывод средств"))
        
    if user.role == MobileUserModel.Role.EXPERT:
        tabs.insert(1, ("services", "Услуги"))
    
    current_tab = safe_get(
        request.GET, "tab", str, 
        default="sessions",
        validate=lambda v: v in [x[0] for x in tabs]
    )
    
    base_context = {
        "user": user,
        "notifications": notifications,
        "tabs": {
            "all": tabs,
            "current": current_tab,
        }
    }
    
    if (
        current_tab == "withdraw" 
        and active_withdraw is not None 
        and session.has_permission(AdminPermission.OWNER)
    ):
        params = {
            "card": {
                "bank": active_withdraw.bank_name,
                "card": " ".join([active_withdraw.card[i:i+4] for i in range(0, len(active_withdraw.card), 4)]),
                "name": active_withdraw.full_name,
            }
        }
        
        if user.role == MobileUserModel.Role.CLIENT:
            balance = user.balance

            params.update({
                "balance": balance,
                "total": balance,
            })
        
        elif user.role == MobileUserModel.Role.EXPERT:
            balance = user.balance
            comission = user.expert_extra.service_commission or 5
            total = balance - (balance * (comission / 100))
            params.update({
                "balance": balance,
                "comission": comission,
                "total": total,
            })
          
        
        return render(request, "admin/user/withdraw.html", {
            **base_context,
            "params": params
        })
    
    elif current_tab == "edit_data":
        return render(request, "admin/user/edit_data.html", base_context)
    
    elif current_tab == "settings":
        settings = {}
        if user.role == MobileUserModel.Role.EXPERT:
            settings.update({
                "comission": user.expert_extra.service_commission or 5
            })
        return render(request, "admin/user/settings.html", {
            **base_context,
            "settings": settings
        })
    
    elif current_tab == "withdraw_history" and session.has_permission(AdminPermission.OWNER):
        return render(request, "admin/user/withdraw_history.html", {
            **base_context,
            "stat": (
                MobileUserWithdrawHistory.objects
                    .filter(
                        user = user,
                        status = MobileUserWithdrawHistory.Status.DONE
                    )
                    .aggregate(
                        total = Sum("count"),
                        profit = Sum("service_profit"),
                    )
            ),
            "withdraw": (
                MobileUserWithdrawHistory.objects
                    .filter(
                        Q(status = MobileUserWithdrawHistory.Status.DONE)
                        | Q(status = MobileUserWithdrawHistory.Status.FAIL),
                        user = user,
                    )
                    .order_by("-created_at")
                    .all()[:20]
            ),
        })
    
    elif (
        current_tab == "services" and
        user.role == MobileUserModel.Role.EXPERT
    ):
        return render(request, "admin/user/expert_services.html", {
            **base_context,
            "services": (
                MobileExpertService.objects
                    .filter(
                        owner_id = user.uuid,
                        status = MobileExpertService.Status.ALIVE,
                    )
                    .all()
            ),
        })
    
    sessions = MobileClientServicePurchase.objects
    if user.role == MobileUserModel.Role.CLIENT:
        sessions = sessions.filter(client_id = user.uuid)
    elif user.role == MobileUserModel.Role.EXPERT:
        sessions = sessions.filter(service__owner_id = user.uuid)
    
    return render(request, "admin/user/actual_sessions.html", {
        **base_context,
        "sessions": (
            sessions
                .filter(
                    Q(status = MobileClientServicePurchase.Status.PRE_PAYMENT)
                    | Q(status = MobileClientServicePurchase.Status.PAID)
                    | Q(status = MobileClientServicePurchase.Status.ACTIVE),
                    service__telegram_link__isnull = True
                )
                .order_by("-date__date", "-hour")
                .all()[:10]
        ),
    })
