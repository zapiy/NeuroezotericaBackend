from typing import TYPE_CHECKING, Optional
from datetime import datetime
from django.db import models

from .expert_extra import MobileUserExpertExtra
from .expert_service_category import MobileExpertServiceCategory
if TYPE_CHECKING:
    from .client_service_purchase import MobileClientServicePurchase
    

class MobileExpertService(models.Model):
    class Meta:
        db_table = 'mobile_expert_service'
    
    class Status(models.TextChoices):
        ALIVE = 'alive'
        ARCHIVE = 'archive'
    
    uuid: str = models.UUIDField(db_index=True, primary_key=True)
    
    owner: MobileUserExpertExtra = models.ForeignKey(
        MobileUserExpertExtra,
        on_delete=models.CASCADE,
        related_name="services"
    )
    
    category: MobileExpertServiceCategory = models.ForeignKey(
        MobileExpertServiceCategory,
        on_delete=models.CASCADE,
        related_name="services"
    )
    
    name: str = models.CharField(max_length=120, null=False)
    price: int = models.IntegerField(null=False)
    description: Optional[str] = models.TextField(max_length=255, null=True)
    
    telegram_link: Optional[str] = models.CharField(max_length=120, null=True)
    
    status: Status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ALIVE,
    )
    
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    
    purchases: models.QuerySet['MobileClientServicePurchase']
