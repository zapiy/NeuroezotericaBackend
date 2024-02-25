from django.db import models
from datetime import datetime

from .user import MobileUserModel


class MobileUserWithdrawHistory(models.Model):
    class Meta:
        db_table = 'mobile_user_withdraw'
    
    class Status(models.TextChoices):
        PROCESSING = 'processing'
        DONE = 'done'
        FAIL = 'fail'
    
    uuid: str = models.UUIDField(db_index=True, primary_key=True)
    
    user: MobileUserModel = models.ForeignKey(
        MobileUserModel, on_delete=models.CASCADE,
        related_name="withdrawal", 
    )
    
    card: str = models.CharField(max_length=20)
    bank_name: str = models.CharField(max_length=100)
    full_name: str = models.CharField(max_length=150)
    count: int = models.IntegerField(null=False, default=1)
    service_profit: int = models.IntegerField(null=False, default=0)
    
    status: Status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    
    created_at: datetime = models.DateTimeField(auto_now_add=True)
