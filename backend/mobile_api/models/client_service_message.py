from typing import Optional
from django.db import models
from datetime import datetime

from .client_service_purchase import MobileClientServicePurchase


class MobileServicePurchaseMessage(models.Model):
    class Meta:
        db_table = 'mobile_service_purchase_messages'
    
    class Type(models.TextChoices):
        TEXT = 'text'
        IMAGE = 'image'
        JOIN = 'join'
        LEAVE = 'leave'
        STARTED = 'started'
        END_CALL = 'end_call'
        ENDED = 'ended'
    
    uuid: str = models.UUIDField(db_index=True, primary_key=True)
    
    from_expert: bool = models.BooleanField(null=False, default=False)
    
    purchase: MobileClientServicePurchase = models.ForeignKey(
        MobileClientServicePurchase,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    
    type: Type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.TEXT,
        null=False
    )
    
    content: Optional[str] = models.TextField(null=True, max_length=1000)
    
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    