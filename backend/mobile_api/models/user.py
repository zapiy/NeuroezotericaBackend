from typing import TYPE_CHECKING, Optional
from datetime import datetime

from django.db import models
if TYPE_CHECKING:
    from .session import MobileSessionModel
    from .expert_extra import MobileUserExpertExtra
    from .client_extra import MobileUserClientExtra
    from .user_withdraw_history import MobileUserWithdrawHistory


class MobileUserModel(models.Model):
    class Meta:
        db_table = 'mobile_user'
    
    class Role(models.TextChoices):
        CLIENT = 'client'
        EXPERT = 'expert'
    
    class Status(models.TextChoices):
        ACTIVE = 'active'
        BLOCKED = 'blocked'
        DELETED = 'delete'

    uuid: str = models.BigAutoField(db_index=True, primary_key=True)
    phone: str = models.CharField(max_length=20, null=False, db_index=True)
    avatar_uuid: str = models.CharField(null=True, max_length=50)
    
    first_name: str = models.CharField(max_length=100, null=False)
    last_name: Optional[str] = models.CharField(max_length=100, null=True)
    
    email: Optional[str] = models.EmailField(unique=True, null=True)

    balance: int = models.IntegerField(null=False, default=0)

    role: Role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    
    selected_role: Role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    status: Status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    password_hash: str = models.CharField(max_length=255, null=False)

    updated_at: datetime = models.DateTimeField(auto_now=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    sessions: models.QuerySet['MobileSessionModel']
    expert_extra: 'MobileUserExpertExtra'
    client_extra: 'MobileUserClientExtra'
    
    withdrawal: models.QuerySet['MobileUserWithdrawHistory']
    