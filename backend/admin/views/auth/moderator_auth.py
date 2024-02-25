from django.http import HttpRequest
from django.shortcuts import redirect
from django.conf import settings

from admin.models import AdminSessionModel, AdminUserModel
from admin.middleware import apply_session_cookies, get_admin_session

ADMIN_PASSWORD = settings.ADMIN_PASSWORD


async def moderator_auth(request: HttpRequest, token: str):
    try:
        user = await AdminUserModel.objects.aget(auth_token = token)
    except AdminUserModel.DoesNotExist:
        return redirect("landing")
    
    session = await get_admin_session(request)
    if session is not None:
        return redirect("admin:users")
    
    session = AdminSessionModel(user = user)
    session.update_csrf_token()
    await session.asave(force_insert=True)
    request._session = session
    return await apply_session_cookies(request, redirect("admin:users"))
