from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from datetime import date, timedelta

from pyqumit import safe_get
from mobile_api.models import MobileUserWithdrawHistory, MobileUserModel
from admin.middleware import admin_is_authenticated
from admin.models import AdminPermission


@admin_is_authenticated(permission_restrict=AdminPermission.OWNER)
async def profit_view(request: HttpRequest):
    query = (
        MobileUserWithdrawHistory.objects
            .filter(
                status = MobileUserWithdrawHistory.Status.DONE,
                user__role = MobileUserModel.Role.EXPERT,
            )
            .order_by("-created_at")
    )
    
    page_id = safe_get(request.GET, "p", int, default=1, validate=lambda v: v > 0)
    paginator = Paginator(query.all(), 15)
    context = {
        "tab": "profit",
        "profit": paginator.get_page(page_id),
        "paginator": {
            "current": page_id,
            "has": paginator.num_pages > 0,
            "range": paginator.get_elided_page_range(),
        },
    }
    if page_id == 1:
        month = date.today().replace(day=1)
        context["stat"] = {
            "expert_count": MobileUserModel.objects.filter(
                role = MobileUserModel.Role.EXPERT
            ).count(),
            **query.aggregate(
                total = Coalesce(Sum("count"), 0),
                profit = Coalesce(Sum("service_profit"), 0),
                withdraw_count = Count("id"),
            ),
            **query
                .filter(
                    created_at__lte = month + timedelta(days=30),
                    created_at__gte = month,
                )
                .aggregate(
                    month_profit = Coalesce(Sum("service_profit"), 0),
                )
        }
    
    return render(request, "admin/stats/profit_view.html", context)
