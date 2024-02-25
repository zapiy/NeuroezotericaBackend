from typing import TYPE_CHECKING, Optional
from django.db import models

from .user import MobileUserModel
if TYPE_CHECKING:
    from .expert_service import MobileExpertService
    from .expert_schedule import MobileExpertSchedule


class MobileUserExpertExtra(models.Model):
    class Meta:
        db_table = 'mobile_user_expert_extra'
    
    user: MobileUserModel = models.OneToOneField(
        MobileUserModel,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="expert_extra"
    )
    
    description: Optional[str] = models.TextField(max_length=255, null=True)
    service_commission: int = models.IntegerField(null=True)
    
    services: models.QuerySet['MobileExpertService']
    schedule: models.QuerySet['MobileExpertSchedule']
