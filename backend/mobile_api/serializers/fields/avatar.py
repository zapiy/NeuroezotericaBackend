from rest_framework.fields import CharField
from django.conf import settings


class AvatarField(CharField):
    
    def __init__(self, default_path: str, path_format: str, *, source: str = "avatar_uuid"):
        super().__init__(read_only=True, source=source)
        assert default_path.startswith('/') and path_format.startswith('/')
        self.default_path = default_path
        self.path_format = path_format
    
    def to_representation(self, value):
        value = super().to_representation(self, value)
        return settings.INTERNET_URL + (
            self.path_format.format(value)
            if value else
            self.default_path
        )
