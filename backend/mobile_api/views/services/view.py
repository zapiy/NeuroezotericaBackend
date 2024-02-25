from datetime import datetime, timedelta
from enum import Enum

from django.http import HttpRequest
from django.conf import settings
from django.db.models.functions import Coalesce, Round
from django.db.models import (
    Avg, Count, Q, When, Case, F, ExpressionWrapper,
    OuterRef, Subquery, DateField, IntegerField, FloatField
)

from adrf.decorators import api_view
from rest_framework.decorators import permission_classes, authentication_classes

from pyqumit import safe_get
from web import CustomJsonResponse, wrap_filters
from mobile_api.authentication import MobileAuthentication, IsAuthenticated
from mobile_api.serializers import PreviewServiceSerializer
from mobile_api.models import (
    MobileExpertServiceCategory, MobileClientServicePurchase, 
    MobileExpertService, MobileUserModel, 
    MobileExpertSchedule
)

class ServicesSortType(Enum):
    RATING = "rating"
    COUNT = "count"

class ExtraServiceSerializer(PreviewServiceSerializer):
    class Meta:
        fields = [
            *PreviewServiceSerializer.Meta.fields,
            "suggest_date", "rating", "lessons"
        ]


@api_view(["GET"])
@authentication_classes([MobileAuthentication])
@permission_classes([IsAuthenticated])
async def services_view(request: HttpRequest):
    user: MobileUserModel = request._user
    
    filters = {}
    expressions = []
    annotations = {}
    
    if user.selected_role == MobileUserModel.Role.CLIENT:
        owner_uuid = safe_get(request.GET, "owner", str, allow_null=True)
        if owner_uuid:
            filters['owner'] = owner_uuid
        else:
            category_uuid = safe_get(request.GET, "category", str, allow_null=True)
            if (
                category_uuid is not None and
                (await MobileExpertServiceCategory.objects.filter(
                    uuid = category_uuid).aexists())
            ):
                filters["category_id"] = category_uuid
            
            sort_by = safe_get(request.GET, "sort_by", ServicesSortType, default=ServicesSortType.RATING)
            is_free_today = safe_get(request.GET, "free_today", bool, default=False)
            
            date_filters = {}
            today = datetime.today().date()
            if not is_free_today:
                from_date = safe_get(
                    request.GET, "from_date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
                    validate=lambda v: v >= today,
                    default=today
                )
                
                to_date = safe_get(
                    request.GET, "to_date", lambda v: datetime.strptime(v, settings.DATE_FORMAT).date(),
                    validate=lambda v: v > from_date,
                    default=from_date + timedelta(days=1)
                )
                
                date_filters["date__gte"] = from_date
                date_filters["date__lt"] = to_date
            else:
                date_filters["date"] = today
            
            expressions.append(
                Q(suggest_date__isnull = False, telegram_link__isnull = True)
                | Q(telegram_link__isnull = False)
            )
            annotations['suggest_date'] = Subquery(
                MobileExpertSchedule.objects
                .annotate(
                    freetimes_count = Count("freetimes"),
                    purchases_count = Count(
                        Case(When(
                            Q(purchases__status = MobileClientServicePurchase.Status.PRE_PAYMENT)
                            | Q(purchases__status = MobileClientServicePurchase.Status.PAID)
                            | Q(purchases__status = MobileClientServicePurchase.Status.ACTIVE),
                            purchases__service__telegram_link__isnull = True,
                            then="purchases"
                        ))
                    ),
                    workhour_count = ExpressionWrapper(
                        F('to_hour') - F('from_hour') - F("freetimes_count") - F("purchases_count"), 
                        output_field=IntegerField()
                    )
                ).filter(
                    owner = OuterRef("owner"),
                    status = MobileExpertSchedule.Status.ON_SCHEDULE,
                    workhour_count__gt = 0,
                    **date_filters
                ).order_by("date").values("date")[:1],
                output_field=DateField(),
            )
            
    elif user.selected_role == MobileUserModel.Role.EXPERT:
        filters['owner'] = user.uuid
    
    return CustomJsonResponse(ExtraServiceSerializer(
        many=True,
        instance = await wrap_filters(
            request, (
                MobileExpertService.objects
                    .annotate(
                        **annotations,
                        rating = Coalesce(
                            Round(Avg(
                            Case(When(
                                    Q(purchases__status = MobileClientServicePurchase.Status.ARCHIVED_FEEDBACK),
                                    then="purchases__rating"
                                ))
                            ), 1), 0,
                            output_field=FloatField()
                        ),
                        lessons = Count(
                            Case(When(
                                Q(
                                    Q(purchases__status = MobileClientServicePurchase.Status.ARCHIVED)
                                    | Q(purchases__status = MobileClientServicePurchase.Status.ARCHIVED_FEEDBACK),
                                    purchases__service__telegram_link__isnull = True
                                )
                                |
                                Q(
                                    purchases__status = MobileClientServicePurchase.Status.PAID,
                                    purchases__service__telegram_link__isnull = False
                                )
                                ,
                                then="purchases"
                            ))
                        ),
                    )
                    .filter(
                        *expressions,
                        **filters,
                        status=MobileExpertService.Status.ALIVE,
                    )
                    .order_by({
                        ServicesSortType.RATING: "-rating",
                        ServicesSortType.COUNT: "-lessons",
                    }.get(sort_by))
            ),
            paginate=True,
            queryable=["name", "owner__user__first_name", "owner__user__last_name"]
        )
    ).data)
