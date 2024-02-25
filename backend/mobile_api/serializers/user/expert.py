from rest_framework.serializers import Field, CharField
from .user import FullUserInfoSerializer


class ExpertInfoSerializer(FullUserInfoSerializer):
    
    description = CharField(
        required=False, source="expert_extra.description", 
        min_length=3, max_length=255
    )
    service_commission = Field(source="expert_extra.service_commission")
    
    class Meta(FullUserInfoSerializer.Meta):
        fields = [
            *FullUserInfoSerializer.Meta.fields,
            "description", "service_commission"
        ]
        read_only_fields = [
            *FullUserInfoSerializer.Meta.read_only_fields,
            "service_commission"
        ]
