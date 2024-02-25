from rest_framework.serializers import Serializer, CharField


class BeginLoginForm(Serializer):
    phone = CharField(min_length=11, max_length=15)


class LoginUserForm(BeginLoginForm):
    password = CharField(min_length=7, max_length=30)
