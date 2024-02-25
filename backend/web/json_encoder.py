from django.utils.functional import Promise
from django.conf import settings

from datetime import datetime, timedelta, date, time
from decimal import Decimal
from uuid import UUID
from enum import Enum

DATETIME_FORMAT = settings.DATETIME_FORMAT
DATE_FORMAT = settings.DATE_FORMAT
TIME_FORMAT = settings.TIME_FORMAT


def custom_json_encoder(obj):
    if isinstance(obj, datetime):
        return obj.strftime(DATETIME_FORMAT)
    elif isinstance(obj, date):
        return obj.strftime(DATE_FORMAT)
    elif isinstance(obj, time):
        return obj.strftime(TIME_FORMAT)
    elif isinstance(obj, timedelta):
        return obj.total_seconds()
    elif isinstance(obj, (Decimal, UUID, Promise)):
        return str(obj)
    elif isinstance(obj, Enum):
        if isinstance(obj.value, str):
            return obj.value
        return obj.name
