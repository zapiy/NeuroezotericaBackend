from django.contrib.auth.hashers import make_password
from rest_framework.fields import CharField


class PasswordField(CharField):
    
    def __init__(
        self, *, 
        min_length: int = 5,
        max_length: int = 30,
        validators: list = None,
        source: str = "password_hash",
    ):
        assert max_length > min_length
        super().__init__(
            write_only=True, required=True,
            validators=validators, source=source
        )
        self.min_length = min_length
        self.max_length = max_length
    
    def to_internal_value(self, value):
        if (
            not isinstance(value, str)
            or value not in range(self.min_length, self.max_length + 1)
        ):
            self.fail('invalid')
            
        return make_password(value.strip())
