from django.shortcuts import render
from django.http import HttpRequest

from mobile_api.models import MobileUserWithdrawHistory
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def withdraw_view(request: HttpRequest):
    return render(request, "admin/stats/withdraw_view.html", {
        "tab": "withdraw",
        "withdraw": (
            MobileUserWithdrawHistory.objects
                .filter(
                    status = MobileUserWithdrawHistory.Status.PROCESSING
                )
                .all()[:20]
        )
    })
