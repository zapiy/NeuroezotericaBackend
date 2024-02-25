from rest_framework.serializers import ModelSerializer
from ...models import MobileServicePurchaseMessage


class MessageSerializer(ModelSerializer):
    class Meta:
        model = MobileServicePurchaseMessage
        fields = ["uuid", "from_expert", "type", "content", "created_at"]
