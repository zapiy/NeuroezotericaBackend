from rest_framework.serializers import *


class FeedbackForm(Serializer):
    rating: int = IntegerField(min_value = 0, max_value = 5)
    feedback: str = CharField(min_length = 1, max_length = 255)
