from typing import TYPE_CHECKING, Optional
from django.db import models
import datetime, uuid

from .expert_service import MobileExpertService
from .client_extra import MobileUserClientExtra
from .expert_schedule import MobileExpertSchedule
if TYPE_CHECKING:
    from .client_service_message import MobileServicePurchaseMessage


class MobileClientServicePurchase(models.Model):
    class Meta:
        db_table = 'mobile_client_service_purchase'
    
    class Status(models.TextChoices):
        PRE_PAYMENT = 'pre_payment'
        PAID = 'paid'
        ACTIVE = 'active'
        ARCHIVED = 'archived'
        ARCHIVED_FEEDBACK = 'archived_feedback'
        CANCELLED = 'cancelled'
    
    uuid: str = models.UUIDField(db_index=True, primary_key=True)
    
    client: MobileUserClientExtra = models.ForeignKey(
        MobileUserClientExtra,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    
    service: MobileExpertService = models.ForeignKey(
        MobileExpertService,
        on_delete=models.CASCADE,
        related_name="purchases"
    )
    
    date: MobileExpertSchedule = models.ForeignKey(
        MobileExpertSchedule,
        on_delete=models.CASCADE,
        related_name="purchases",
        null=True
    )
    
    hour: int = models.IntegerField(null=True)
    
    status: Status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRE_PAYMENT,
    )
    
    real_price: int = models.IntegerField(null=False, default=0)
    price: int = models.IntegerField(null=False, default=0)
    rating: Optional[int] = models.IntegerField(null=True)
    feedback: Optional[str] = models.TextField(null=True, max_length=255)
    
    confirm_hash: str = models.UUIDField(null=False, default=uuid.uuid4)
    payment_link: Optional[str] = models.CharField(null=True, max_length=150)
    
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    
    messages: models.QuerySet['MobileServicePurchaseMessage']
