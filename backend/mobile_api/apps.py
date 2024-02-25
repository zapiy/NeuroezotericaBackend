from django.apps import AppConfig


class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mobile_api'
    models_module = "mobile_api.models"
