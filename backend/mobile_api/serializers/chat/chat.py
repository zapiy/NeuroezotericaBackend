from rest_framework.serializers import ModelSerializer, DateField
from ...models import MobileClientServicePurchase
from ..user import PreviewUserInfoSerializer
from ..service import PreviewServiceSerializer


class ChatSerializer(ModelSerializer):
    
    client = PreviewUserInfoSerializer()
    service = PreviewServiceSerializer()
    date = DateField(source="date.date")
    
    class Meta:
        model = MobileClientServicePurchase
        fields = [
            "uuid", "client", "service", 
            "date", "hour", "status", "price", 
            "created_at"
        ]


class ArchivedChatSerializer(ChatSerializer):
    class Meta(ChatSerializer.Meta):
        fields = [
            *ChatSerializer.Meta.fields,
            "rating", "feedback",
        ]
