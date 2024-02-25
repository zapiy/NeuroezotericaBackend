from rest_framework.serializers import ModelSerializer
from ...models import MobileExpertServiceCategory


class ServiceCategorySerializer(ModelSerializer):
    class Meta:
        model = MobileExpertServiceCategory
        fields = ["uuid", "name"]
