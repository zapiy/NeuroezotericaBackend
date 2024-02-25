from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.conf import settings

from admin.models import AdminSessionModel
from admin.middleware import apply_session_cookies, get_admin_session

ADMIN_PASSWORD = settings.ADMIN_PASSWORD


async def owner_auth(request: HttpRequest):
    if request.method == "POST":
        password = request.POST.get("password", None)
        if password is not None and ADMIN_PASSWORD == password:
            session = AdminSessionModel()
            session.update_csrf_token()
            await session.asave(force_insert=True)
            request._session = session
            return await apply_session_cookies(request, redirect("admin:main"))
    
    session = await get_admin_session(request)
    if session is not None:
        return redirect("admin:main")
        
    return render(request, "admin/auth.html")
