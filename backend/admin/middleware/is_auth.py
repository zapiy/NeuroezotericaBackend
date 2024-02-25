from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings

from middleware import wrap_middleware
from ..models import AdminSessionModel, AdminPermission

SESSION_COOKIE_NAME = "admin_session_key"
CSRF_COOKIE_NAME = "admin_csrf_token"
CSRF_HEADER_NAME = "X-CSRF-TOKEN"


async def _forbidden():
    resp = HttpResponseRedirect("/")
    resp.delete_cookie(SESSION_COOKIE_NAME)
    resp.delete_cookie(CSRF_COOKIE_NAME)
    return resp


async def set_cookie(
    response: HttpResponse, name: str, value: str, *, 
    http_only: bool = True
):
    response.set_cookie(
        name, value,
        max_age=settings.SESSION_COOKIE_AGE,
        domain=settings.SESSION_COOKIE_DOMAIN,
        path="/",
        secure=settings.SESSION_COOKIE_SECURE,
        httponly=http_only,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )


async def apply_session_cookies(request: HttpRequest, response: HttpResponse):
    session: AdminSessionModel = request._session
    
    await set_cookie(response, SESSION_COOKIE_NAME, session.session_key)
    await set_cookie(response, CSRF_COOKIE_NAME, session.csrf_token, http_only=False)
    return response


async def get_admin_session(request: HttpRequest):
    session_key = request.COOKIES.get(SESSION_COOKIE_NAME, None)
    csrf_token = request.COOKIES.get(CSRF_COOKIE_NAME, None)
    
    if session_key is None or csrf_token is None:
        return None
    
    try:
        session = await AdminSessionModel.objects.aget(session_key=session_key)
    except AdminSessionModel.DoesNotExist:
        return None
    
    if session.csrf_token != csrf_token:
        await session.adelete()
        return None
    
    return session


def admin_is_authenticated(permission_restrict: AdminPermission = None):
    async def middleware(request: HttpRequest, next):
        session = await get_admin_session(request)
        
        if session is None:
            return await _forbidden()
        
        if request.method != 'GET':
            csrf_token = request.headers.get(CSRF_HEADER_NAME, None)
            if csrf_token != session.csrf_token:
                return HttpResponseForbidden("Incorrect CSRF token")
        
        session.update_csrf_token()
        
        if permission_restrict is not None:
            if not session.has_permission(permission_restrict):
                return HttpResponseForbidden("Has no permissions!")
        
        request._session = session
        request._user = session.user
        resp = await apply_session_cookies(request, await next())
        await session.asave(force_update=True)
        return resp
    return wrap_middleware(middleware)
