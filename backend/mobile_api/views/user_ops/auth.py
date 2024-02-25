from django.http import HttpRequest
from django.contrib.auth.hashers import make_password, check_password
import logging

from adrf.decorators import api_view

from pyqumit import safe_get
from mobile_api.utils import ResponseType, typed_response, get_session_from_request
from mobile_api.models import MobileUserModel, MobileSessionModel, MobileUserClientExtra, MobileClientReferalRelation
from mobile_api.serializers import BeginLoginForm, LoginUserForm, RegisterUserForm

logger = logging.getLogger("mobile_auth")
logger.setLevel(logging.DEBUG)

@api_view(["GET", "POST"])
async def auth(request: HttpRequest):
    operation = request.GET.get("op", None)
    if operation == "begin":
        form = BeginLoginForm(data=request.DATA)
        
        if not form.is_valid():
            return typed_response(ResponseType.INVALID_FIELDS, status=409)
        
        phone = form.data['phone']
        logger.debug(f"Begin with phone: {phone}")
        
        if "Authorization" in request.headers:
            logger.debug(f"[{phone}] => Has session header")
            session = await get_session_from_request(request)
            if session is not None:
                await session.adelete()
            del session
        
        logger.debug(f"[{phone}] => Create new session")

        if await MobileUserModel.objects.filter(phone = phone).aexists():
            return typed_response(ResponseType.REQUIRED_LOGIN)
            
        session = MobileSessionModel()
        session.extra = { "phone": phone }
        session.status = MobileSessionModel.Status.REGISTER
        await session.asave(force_insert=True)
        
        return typed_response(ResponseType.REQUIRED_REGISTER, data = { "bearer": session.auth_token })
        
    elif operation == "login":
        form = LoginUserForm(data=request.DATA)
        
        if not form.is_valid():
            return typed_response(ResponseType.INVALID_FIELDS)
        
        try:
            user = await MobileUserModel.objects.aget(phone = form.data['phone'])
        except MobileUserModel.DoesNotExist:
            return typed_response(ResponseType.INVALID_FIELDS, status=409)
            
        if not check_password(form.data['password'], user.password_hash):
            return typed_response(ResponseType.INVALID_FIELDS, status=409)
        elif user.status == MobileUserModel.Status.BLOCKED:
            return typed_response(ResponseType.BLOCKED, status=403)
        
        session = MobileSessionModel(
            user=user,
            status = MobileSessionModel.Status.ACTIVE
        )
        await session.asave(force_insert=True)
        return typed_response(ResponseType.LOGGED_IN, data = { "bearer": session.auth_token })
    
    elif "Authorization" in request.headers:
        session = await get_session_from_request(request)
        if session is None or session.status == session.Status.EXPIRED:
            return typed_response(ResponseType.SESSION_EXPIRED, status=401)
        
        logger.debug(f"Begin session with token [Operation: {operation}, Status: {session.status}]")
        
        if operation == "register" and session.status == session.Status.REGISTER:
            form = RegisterUserForm(data=request.DATA)
            
            if not form.validate():
                return typed_response(ResponseType.INVALID_FIELDS, status=409)
            
            user = form.instance = MobileUserModel(
                phone = session.extra.get("phone"),
                client_extra = MobileUserClientExtra()
            )
            form.save()
            
            logger.info("Success registration of " + session.extra["phone"])
            
            session.user = user
            session.status = session.Status.ACTIVE
            session.extra = None
            
            await user.asave(force_insert=True)
            await user.client_extra.asave(force_insert=True)
            await session.asave(force_update=True)
            
            referal_code = safe_get(
                request.DATA, "referal_code", str, validate=lambda v: len(v) == 8)
            
            if referal_code:
                try:
                    await MobileClientReferalRelation(
                        user = user.client_extra,
                        by = await MobileUserClientExtra.objects.aget(
                            referal_code = referal_code
                        )
                    ).asave(force_insert=True)
                except MobileUserClientExtra.DoesNotExist:
                    pass
            
            return typed_response(ResponseType.LOGGED_IN)
        
        elif session is None or session.status != session.Status.ACTIVE:
            await session.adelete()
            return typed_response(ResponseType.SESSION_EXPIRED, status=401)
        
        elif session.user.status != session.user.Status.ACTIVE:
            await session.adelete()
            return typed_response(ResponseType.BLOCKED, status=403)
            
        elif operation == "validate":
            return typed_response(
                ResponseType.LOGGED_IN, 
                data={
                    "role": session.user.role, 
                    "selected_role": session.user.selected_role
                }
            )
        
        elif operation == "switch_role":
            if session.user.role != session.user.Role.EXPERT:
                return typed_response(ResponseType.RESTRICT, status=403)
            
            session.user.selected_role = (
                MobileUserModel.Role.CLIENT
                if session.user.selected_role == MobileUserModel.Role.EXPERT else 
                MobileUserModel.Role.EXPERT 
            )
            await session.user.asave(force_update=True)
            
            return typed_response(
                ResponseType.OKAY, 
                data={
                    "role": session.user.role, 
                    "selected_role": session.user.selected_role
                }
            )
    
    return typed_response(ResponseType.UNKNOWN_OPERATION, status=406)
