from typing import TYPE_CHECKING
from django.db import models

if TYPE_CHECKING:
    from .expert_service import MobileExpertService
    

class MobileExpertServiceCategory(models.Model):
    class Meta:
        db_table = 'mobile_expert_service_category'
    
    uuid: str = models.UUIDField(db_index=True, primary_key=True) 
    name: str = models.CharField(max_length=120, null=False, unique=True)
    
    services: models.QuerySet['MobileExpertService']
