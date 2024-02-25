from datetime import datetime, date, timedelta

from django.http import HttpRequest
from django.db.models import Q, DateField
from django.db.models.functions import Coalesce
from django.conf import settings

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from web import CustomJsonResponse, wrap_filters
from pyqumit import safe_get
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.models import MobileUserModel, MobileClientServicePurchase
from mobile_api.serializers import ChatSerializer


@api_view(['GET'])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def chat_view(request: HttpRequest):
    user: MobileUserModel = request._user
    
    filters = {}
    expressions = []
    if user.selected_role == MobileUserModel.Role.CLIENT:
        date_delta = date.today() - timedelta(days=2)
        filters["client"] = user.client_extra
        expressions.extend([
            Q(status = MobileClientServicePurchase.Status.PRE_PAYMENT)
            | Q(
                (Q(service__telegram_link__isnull = True)
                | Q(
                    service__telegram_link__isnull = False,
                    schedule__gte = date_delta
                )),
                status = MobileClientServicePurchase.Status.PAID
            )
            | Q(status = MobileClientServicePurchase.Status.ACTIVE)
            | Q(status = MobileClientServicePurchase.Status.ARCHIVED),
        ])
        
    elif user.selected_role == MobileUserModel.Role.EXPERT:
        date_filter = safe_get(
            request.GET, "date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
            validate=lambda v: v >= datetime.today().date()
        )
        if date_filter:
            filters['schedule'] = date_filter
        filters.update({
            "service__owner": user.expert_extra,
            "service__telegram_link__isnull": True,
        })
        expressions.extend([
            Q(status = MobileClientServicePurchase.Status.PAID)
            | Q(status = MobileClientServicePurchase.Status.ACTIVE)
        ])

    return CustomJsonResponse(ChatSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileClientServicePurchase.objects
                    .filter(*expressions, **filters)
                    .annotate(
                        schedule = Coalesce(
                            "date__date", "created_at",
                            output_field=DateField()
                        )
                    )
                    .order_by("-schedule")
            ),
            paginate=True
        )
    ).data)
