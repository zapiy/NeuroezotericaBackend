from urllib.parse import parse_qs

from ..models import MobileSessionModel


async def get_session_from_ws_scope(scope: dict):
    try:
        params: dict = parse_qs(dict(scope)["query_string"])
        token: str = params.get(b"auth_token", None)[0].decode("utf-8")
    except:
        return None

    if token is None or len(token) < 16:
        return None
    
    try:
        session = await MobileSessionModel.objects.aget(auth_token = token)
    except MobileSessionModel.DoesNotExist:
        return None
    
    return session
