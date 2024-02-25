from channels.security.websocket import WebsocketDenier

from middleware import wrap_middleware
from ..utils import get_session_from_ws_scope


def mobile_ws_is_authenticated():
    async def middleware(scope: dict, next):
        session = await get_session_from_ws_scope(scope)
        if (
            session is None 
            or session.status != session.Status.ACTIVE 
            or session.user is None
        ):
            return WebsocketDenier()
        
        scope["session"] = session
        return await next()
    return wrap_middleware(middleware)
