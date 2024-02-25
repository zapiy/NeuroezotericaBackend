from django.http import HttpRequest

from ..models import MobileSessionModel


async def get_session_from_request(request: HttpRequest):
    token: str = request.headers.get("Authorization", None)
    if (
        token is None
        or len(token) < 10
        or not token.startswith("Bearer ")
    ):
        return None
    
    token = token[7:]
    
    try:
        session = await MobileSessionModel.objects.aget(auth_token = token)
    except MobileSessionModel.DoesNotExist:
        return None
    
    return session