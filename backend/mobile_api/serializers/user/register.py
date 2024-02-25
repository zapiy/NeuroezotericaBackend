from ..fields import PasswordField
from .client import ClientInfoSerializer


class RegisterUserForm(ClientInfoSerializer):
    password = PasswordField()
