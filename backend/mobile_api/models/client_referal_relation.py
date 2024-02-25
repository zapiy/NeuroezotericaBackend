from datetime import datetime
from django.db import models

from .client_extra import MobileUserClientExtra


class MobileClientReferalRelation(models.Model):
    class Meta:
        db_table = 'mobile_user_client_referal_relation'
        unique_together = (("user", "by"),)
        
    user: MobileUserClientExtra = models.OneToOneField(
        MobileUserClientExtra,
        on_delete=models.CASCADE,
        related_name="referred_by",
        null=False
    )
    
    by: MobileUserClientExtra = models.ForeignKey(
        MobileUserClientExtra,
        on_delete=models.CASCADE,
        related_name="invitations",
        null=False
    )
    
    points: int = models.IntegerField(null=False, default=0)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    