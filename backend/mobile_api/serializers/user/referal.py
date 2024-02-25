from rest_framework.serializers import ModelSerializer, Field
from ...models import MobileClientReferalRelation
from .user import PreviewUserInfoSerializer


class ReferalUserInfoSerializer(ModelSerializer):

    user = PreviewUserInfoSerializer()
    refered_at = Field(source='created_at')

    class Meta:
        model = MobileClientReferalRelation
        fields = ["user", "points", "refered_at"]
