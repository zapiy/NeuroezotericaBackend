from rest_framework.serializers import ModelSerializer, CharField
from ...models import MobileUserWithdrawHistory


class WithdrawSerializer(ModelSerializer):
    
    card = CharField(min_length=15, max_length=20)
    bank_name = CharField(min_length=3, max_length=100)
    full_name = CharField(min_length=5, max_length=150)
    
    class Meta:
        model = MobileUserWithdrawHistory
        fields = [
            "uuid", "card", "bank_name", 
            "full_name", "count", "service_profit", 
            "status", "created_at"
        ]
        read_only_fields = [
            "uuid", "count", "service_profit", 
            "status", "created_at"
        ]
