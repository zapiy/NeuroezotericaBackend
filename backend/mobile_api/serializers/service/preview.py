from rest_framework.serializers import ModelSerializer
from ...models import MobileExpertService
from ..fields import StringIsEmptyField
from ..user import PreviewUserInfoSerializer
from .category import ServiceCategorySerializer


class PreviewServiceSerializer(ModelSerializer):
    
    owner = PreviewUserInfoSerializer()
    category = ServiceCategorySerializer()
    in_telegram = StringIsEmptyField(source='telegram_link')
    
    class Meta:
        model = MobileExpertService
        fields = [
            "uuid", "name", "category", "owner", "price", 
            "description", "in_telegram", "created_at"
        ]
