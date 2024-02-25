from django.urls import path
from channels.routing import URLRouter

from .authentication import mobile_ws_is_authenticated
from . import ws_consumers
from . import views

app_name = 'mobile_api'

urlpatterns = [
    path('locales', view=views.locales),
    path('i10n/<str:code>', view=views.locale),
    
    path('auth', view=views.auth),
    path('inviting/<str:code>', view=views.inviting_preview),
    
    path('user/info', view=views.user_info),
    path('referals', view=views.referals_view),
    path('change/avatar', view=views.change_avatar),
    path('change/password', view=views.change_password),
    path('logout', view=views.logout),
    
    path('services', view=views.services_view),
    path('services/categories', view=views.services_category_view),
    
    path('service', view=views.service_item),
    path('service/<str:uuid>/feedback', view=views.service_feedback_view),
    
    path('news', view=views.news_view),
    path('withdraw', view=views.withdraw_view),
    
    path('schedule', view=views.schedule_day),
    path('schedule/sessions/<str:uuid>/cancel', view=views.schedule_sessions_cancel),
    path('schedule/push', view=views.schedule_push),
    path('schedule/<str:uuid>/times', view=views.schedule_times),
    path('schedule/<str:uuid>/cancel', view=views.schedule_cancel),
    
    path('chats', view=views.chat_view),
    path('chats/archive', view=views.archive_view),
    
    path('messages/<str:uuid>', view=views.MessagesView.as_view()),
    path('chat/<str:uuid>/start', view=views.chat_start),
    path('chat/<str:uuid>/finish', view=views.chat_finish),
    path('chat/<str:uuid>/feedback', view=views.chat_send_feedback),
    
    path('3party/prodamus/confirm/<str:uuid>', view=views.prodamus_confirm),
]

ws_router = URLRouter([
    # path("notifications/", ws_mobile_is_authenticated()(ws_consumers.NotificationConsumer.as_asgi())),
    path("chat/<int:id>/", mobile_ws_is_authenticated()(ws_consumers.ChatConsumer.as_asgi())),
])
