from rest_framework.serializers import ModelSerializer
from ...models import MobileNewsModel
from ..fields import AvatarField


class NewsSerializer(ModelSerializer):
    
    wallpaper = AvatarField(
        default_path="/static/media_defaults/wallpaper_uuid.jpg",
        path_format="/media/news_wallpaper/{0}.jpg",
        source="wallpaper_uuid"
    )
    
    class Meta:
        model = MobileNewsModel
        fields = ["uuid", "wallpaper", "title", "content", "created_at"]
