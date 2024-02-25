from typing import TYPE_CHECKING
from django.db import models
import datetime

from .expert_extra import MobileUserExpertExtra
if TYPE_CHECKING:
    from .client_service_purchase import MobileClientServicePurchase


class MobileExpertSchedule(models.Model):
    class Meta:
        db_table = 'mobile_expert_schedule'
        unique_together = (("owner", "date"),)
    
    class Status(models.TextChoices):
        ON_SCHEDULE = 'on_schedule'
        OUTLET = 'outlet'
    
    owner: MobileUserExpertExtra = models.ForeignKey(
        MobileUserExpertExtra,
        on_delete=models.CASCADE,
        related_name="schedule"
    )
    
    date: datetime.date = models.DateField()
    
    status: Status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ON_SCHEDULE,
    )
    
    from_hour: int = models.IntegerField(null=False, default=0)
    to_hour: int = models.IntegerField(null=False, default=20)
    
    purchases: models.QuerySet['MobileClientServicePurchase']
    freetimes: models.QuerySet['MobileExpertScheduleFreetime']


class MobileExpertScheduleFreetime(models.Model):
    class Meta:
        db_table = 'mobile_expert_schedule_freetime'
        unique_together = (("date", "hour"),)
    
    date: MobileExpertSchedule = models.ForeignKey(
        MobileExpertSchedule,
        on_delete=models.CASCADE,
        related_name="freetimes"
    )
    
    hour: int = models.IntegerField(null=False, default=1)
