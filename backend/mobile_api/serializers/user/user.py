from rest_framework.serializers import ModelSerializer, EmailField, CharField
from ...models import MobileUserModel
from ..fields import AvatarField


class PreviewUserInfoSerializer(ModelSerializer):
    
    avatar = AvatarField(
        default_path="/static/media_defaults/avatar.jpg",
        path_format="/media/avatar/{0}.jpg"
    )
    first_name = CharField(required=True, min_length=3, max_length=100)
    last_name = CharField(min_length=3, max_length=100)
    email = EmailField()
    phone = CharField(read_only=True)
    
    class Meta:
        model = MobileUserModel
        fields = [
            "uuid", "avatar", "first_name", "last_name", 
            "phone", "email", "created_at"
        ]
        read_only_fields = ['uuid', 'avatar', 'created_at']


class FullUserInfoSerializer(PreviewUserInfoSerializer):
    class Meta(PreviewUserInfoSerializer.Meta):
        fields = [
            *PreviewUserInfoSerializer.Meta.fields,
            "balance", "role", "selected_role",
        ]
        read_only_fields = [
            *PreviewUserInfoSerializer.Meta.read_only_fields,
            "balance", "role", "selected_role",
        ]
