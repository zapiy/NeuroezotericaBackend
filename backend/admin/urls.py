from django.urls import path

from . import views

app_name = 'admin'

urlpatterns = [
    path("", views.owner_auth, name="auth"),
    path("@/<str:token>", views.moderator_auth, name="auth_moderator"),
    path("withdraw", views.withdraw_view, name="main"),
    path("stats/profit", views.profit_view, name="profit_stats"),
    
    path("users", views.users_view, name="users"),
    path("user/<str:uuid>/settings", views.user_settings, name="user_settings"),
    path("user/<str:uuid>/withdrawal", views.user_withdrawal, name="user_withdrawal"),
    path("user/<str:uuid>/switch", views.user_switch_role, name="user_switch"),
    path("user/<str:uuid>/block", views.user_switch_block, name="user_block"),
    path("user/<str:uuid>/edit", views.user_edit_data, name="user_edit_data"),
    path("user/<str:uuid>", views.user_item, name="user"),
    
    path("news/<str:uuid>", views.news_item, name="news_item"),
    path("news", views.news_view, name="news"),
    
    path("categories", views.categories_view, name="categories"),
    path("category/<str:uuid>", views.category, name="category"),
    
    path("translation", views.translate_view, name="translation"),
    path("translate/<str:code>", views.translate, name="translate"),
    path("translate/<str:code>/settings", views.translate_settings, name="translate_settings"),
    path("translate/<str:code>/text/<str:text_code>", views.translate_word, name="translate_word"),
    
    path("moderators", views.moderators_view, name="moderators"),
    path("moderator/<str:key>", views.moderator, name="moderator"),
]
