from enum import Enum
from typing import Optional
from web import CustomJsonResponse


class ResponseType(Enum):
    UNKNOWN_OPERATION = "unknown_operation"
    
    INVALID_FIELDS = "invalid_fields"
    REQUIRED_LOGIN = "required_login"
    REQUIRED_REGISTER = "required_register"
    
    TOO_FAST = "not_too_fast"
    SESSION_EXPIRED = "session_expired"
    BLOCKED = "blocked"
    LOGGED_IN = "logged_in"
    OKAY = "okay"
    RESTRICT = "restrict"


TYPED_DEFAULT_STATUSES = {
    ResponseType.INVALID_FIELDS: 422,
    ResponseType.TOO_FAST: 429,
    ResponseType.RESTRICT: 403,
    ResponseType.BLOCKED: 403,
    ResponseType.SESSION_EXPIRED: 401,
    ResponseType.UNKNOWN_OPERATION: 406,
}

def typed_response(type: ResponseType, *, data: Optional[dict] = None, status: int = None):
    return CustomJsonResponse(
        { "type": type, "data": data }, 
        status = status or TYPED_DEFAULT_STATUSES.get(type, 200)
    )
