from typing import Optional
from datetime import datetime
from django.db import models


class MobileNewsModel(models.Model):
    class Meta:
        db_table = 'mobile_news'

    uuid: str = models.UUIDField(db_index=True, primary_key=True)
    wallpaper_uuid: Optional[str] = models.CharField(null=True, max_length=50)
    
    title: str = models.CharField(max_length=120, null=False)
    content: Optional[str] = models.TextField(max_length=1000, null=True)

    created_at: datetime = models.DateTimeField(auto_now_add=True)
