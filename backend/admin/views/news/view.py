from django.shortcuts import render
from django.http import HttpRequest

from mobile_api.models import MobileNewsModel
from ...middleware import admin_is_authenticated


@admin_is_authenticated()
async def news_view(request: HttpRequest):
    return render(request, "admin/news/view.html", {
        "tab": "news",
        "news": MobileNewsModel.objects.order_by("-created_at").all()[:20]
    })
    