from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from . import views
from mobile_api.urls import ws_router as mobile_ws_router


urlpatterns = [
    path('', views.landing, name="landing"),
    path('admin/', include('admin.urls')),
    path('@/api/mobile/', include('mobile_api.urls')),
]

websocket_urlpatterns = [
    path("ws/mobile/", mobile_ws_router),
]

if settings.DEBUG:
    if settings.MEDIA_ROOT != '/':
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
