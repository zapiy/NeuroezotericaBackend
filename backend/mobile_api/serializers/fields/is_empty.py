from rest_framework.fields import BooleanField


class StringIsEmptyField(BooleanField):
    def __init__(self, source: str):
        super().__init__(read_only=True, source=source)
        
    def to_representation(self, value):
        assert isinstance(value, (str, type(None)))
        return bool(value)
