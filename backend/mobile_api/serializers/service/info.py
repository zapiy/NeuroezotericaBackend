from rest_framework.serializers import ModelSerializer, CharField, IntegerField
from ...models import MobileExpertService
from .category import ServiceCategorySerializer


class ServiceInfoForm(ModelSerializer):
    
    category = ServiceCategorySerializer()
    name = CharField(min_length=5, max_length=100)
    price = IntegerField(min_value=0, max_value=10000000)
    description = CharField(min_length=10, max_length=255)
    telegram_link = CharField(min_length=3, max_length=50, required=False)
    
    class Meta:
        model = MobileExpertService
        fields = [
            "uuid", "name", "category", "price", 
            "description", "telegram_link", "created_at"
        ]
        read_only_fields = ['uuid', 'category', 'created_at']
