from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

from ..models import MobileUserModel
from ..utils import get_session_from_request


class MobileAuthentication(BaseAuthentication):
    async def authenticate(self, request):
        session = await get_session_from_request(request)
        if (
            session is not None
            and session.status == session.Status.ACTIVE
            and session.user_id is not None
        ):
            request._session = session
            request._user = session.user
            return session.user, None
        request._session = request._user = None
        return None, None


class IsAuthenticated(BasePermission):
    
    def has_permission(self, request, view):
        user: MobileUserModel = request._user
        return user is not None


class IsAuthenticatedAsClient(BasePermission):
    
    def has_permission(self, request, view):
        user: MobileUserModel = request._user
        return (user is not None and user.selected_role == MobileUserModel.Role.CLIENT)


class IsAuthenticatedAsExpert(BasePermission):
    
    def has_permission(self, request, view):
        user: MobileUserModel = request._user
        return (user is not None and user.selected_role == MobileUserModel.Role.EXPERT)
