from fastapi import HTTPException, Depends, status
from app.api.routes.auth import get_current_user
from app.models.trade_models import User

# Permission constants
CASE_READ = "case:read"
CASE_WRITE = "case:write"
CASE_DELETE = "case:delete"
DOCUMENT_UPLOAD = "document:upload"
DOCUMENT_DELETE = "document:delete"
CHAT_SEND = "chat:send"
MEMBER_INVITE = "member:invite"
MEMBER_MANAGE = "member:manage"
ORG_UPDATE = "org:update"
REPORT_GENERATE = "report:generate"
WORKFLOW_APPROVE = "workflow:approve"

# Role -> Permissions mapping
ROLE_PERMISSIONS = {
    "VIEWER": {
        CASE_READ,
        CHAT_SEND,
    },
    "ANALYST": {
        CASE_READ,
        DOCUMENT_UPLOAD,
        CHAT_SEND,
        REPORT_GENERATE,
    },
    "TRADE_MANAGER": {
        CASE_READ,
        CASE_WRITE,
        CASE_DELETE,
        DOCUMENT_UPLOAD,
        DOCUMENT_DELETE,
        CHAT_SEND,
        REPORT_GENERATE,
        WORKFLOW_APPROVE,
    },
    "ADMIN": {
        CASE_READ,
        CASE_WRITE,
        CASE_DELETE,
        DOCUMENT_UPLOAD,
        DOCUMENT_DELETE,
        CHAT_SEND,
        REPORT_GENERATE,
        WORKFLOW_APPROVE,
        MEMBER_INVITE,
        MEMBER_MANAGE,
    },
    "OWNER": {
        CASE_READ,
        CASE_WRITE,
        CASE_DELETE,
        DOCUMENT_UPLOAD,
        DOCUMENT_DELETE,
        CHAT_SEND,
        REPORT_GENERATE,
        WORKFLOW_APPROVE,
        MEMBER_INVITE,
        MEMBER_MANAGE,
        ORG_UPDATE,
    },
}

def require_permission(permission: str):
    """
    FastAPI dependency that checks if the current user has the required permission.
    """
    def permission_checker(user: User = Depends(get_current_user)):
        # Normalize role to match the mapping keys
        user_role = user.role.upper() if user.role else "VIEWER"

        # If the role isn't in our map, default to the most restrictive role (VIEWER)
        allowed_permissions = ROLE_PERMISSIONS.get(user_role, ROLE_PERMISSIONS["VIEWER"])

        if permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return user

    return permission_checker
