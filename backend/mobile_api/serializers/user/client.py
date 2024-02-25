from rest_framework.serializers import Field
from .user import FullUserInfoSerializer


class ClientInfoSerializer(FullUserInfoSerializer):
    
    referal_code = Field(source="client_extra.referal_code")
    bonuses = Field(source="client_extra.bonuses")
    
    class Meta(FullUserInfoSerializer.Meta):
        fields = [
            *FullUserInfoSerializer.Meta.fields,
            "referal_code", "bonuses"
        ]
        read_only_fields = [
            *FullUserInfoSerializer.Meta.read_only_fields,
            "referal_code", "bonuses"
        ]
