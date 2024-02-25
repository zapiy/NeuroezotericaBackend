from django.shortcuts import render
from django.db.models import Value, Count, Case, When, IntegerField, CharField
from django.db.models.functions import Concat, Lower
from django.core.paginator import Paginator
from django.http import HttpRequest

from pyqumit import safe_get
from mobile_api.models import MobileUserModel
from ...middleware import admin_is_authenticated


@admin_is_authenticated()
async def users_view(request: HttpRequest):
    query = (
        MobileUserModel.objects.order_by("-created_at")
            .annotate(
                relerals_count = Case(
                    When(
                        role = MobileUserModel.Role.CLIENT,
                        then = Count("client_extra__invitations"),
                    ),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
    )
    search_query = safe_get(request.GET, "q", str, prepare=lambda v: v.strip(), validate=lambda v: len(v) > 0)
    if search_query is not None:
        query = (
            query
                .annotate(
                    query = Lower(Concat(
                        "first_name", Value(" "), 
                        "last_name", Value(" +"), "phone"
                    ), output_field=CharField())
                )
                .filter(query__contains=search_query.lower())
                .all()[:20]
        )
        
        return render(request, "admin/user/view.html", {
            "tab": "users",
            "users": query,
            "query": search_query,
        })
        
    page_id = safe_get(request.GET, "p", int, default=1, validate=lambda v: v > 0)
    
    paginator = Paginator(query.all(), 15)
    
    return render(request, "admin/user/view.html", {
        "tab": "users",
        "users": paginator.get_page(page_id),
        "paginator": {
            "current": page_id,
            "has": paginator.num_pages > 0,
            "range": paginator.get_elided_page_range(),
        },
    })
