from typing import TYPE_CHECKING
from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from pyqumit.string import generate_token
if TYPE_CHECKING:
    from .session import AdminSessionModel


def get_new_auth_token() -> str:
    while True:
        token = generate_token(32) + "_" + generate_token(64)
        if not AdminUserModel.objects.filter(auth_token=token).exists():
            return token


class AdminUserModel(models.Model):
    class Meta:
        db_table = 'admin_user'
        unique_together = (("key_name", "auth_token"),)
    
    key_name: str = models.CharField(_('key name'), max_length=50, null=True)
    auth_token = models.CharField(_('auth token'), max_length=100, db_index=True, default=get_new_auth_token)

    sessions: models.QuerySet['AdminSessionModel']
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    