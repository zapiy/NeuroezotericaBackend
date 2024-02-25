from typing import TYPE_CHECKING, Optional
from django.db import models
from pyqumit.string import generate_token
import string

from .user import MobileUserModel
if TYPE_CHECKING:
    from .client_service_purchase import MobileClientServicePurchase
    from .client_referal_relation import MobileClientReferalRelation


def get_new_referal_code() -> str:
    while True:
        code = generate_token(8, char_src=string.ascii_uppercase + string.digits)
        if not MobileUserClientExtra.objects.filter(referal_code=code).exists():
            return code


class MobileUserClientExtra(models.Model):
    class Meta:
        db_table = 'mobile_user_client_extra'
        
    user: MobileUserModel = models.OneToOneField(
        MobileUserModel,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="client_extra"
    )
    
    referal_code: str = models.CharField(
        max_length=10, db_index=True, 
        unique=True, null=False, default=get_new_referal_code
    )
    
    bonuses: int = models.IntegerField(null=False, default=0)
    
    purchases: models.QuerySet['MobileClientServicePurchase']
    
    referred_by: Optional['MobileClientReferalRelation']
    invitations: models.QuerySet['MobileClientReferalRelation']
    