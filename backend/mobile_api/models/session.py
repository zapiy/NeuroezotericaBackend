from datetime import datetime
from typing import Optional
from django.db import models
import string

from pyqumit.string import generate_token
from .user import MobileUserModel


def get_new_auth_token() -> str:
    while True:
        token = generate_token(32) + "_" + generate_token(64)
        if not MobileSessionModel.objects.filter(auth_token=token).exists():
            return token

class MobileSessionModel(models.Model):
    class Meta:
        db_table = 'mobile_session'
    
    class Status(models.TextChoices):
        REGISTER = 'register'
        ACTIVE = 'active'
        EXPIRED = 'expired'
    
    auth_token: str = models.CharField(primary_key=True, db_index=True, max_length=120, default=get_new_auth_token)
    
    user: Optional[MobileUserModel] = models.ForeignKey(
        MobileUserModel, related_name="sessions", 
        on_delete=models.CASCADE, null=True,
    )
    
    status: Status = models.CharField(
        max_length=15,
        choices=Status.choices,
    )
    
    extra: dict = models.JSONField(null=True)
    
    updated_at: datetime = models.DateTimeField(auto_now=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    
    def gen_new_sms_code(self) -> str:
        return generate_token(4, char_src=string.digits)
    