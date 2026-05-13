"""Auth-ready scaffold — enforcement disabled until AUTH_ENFORCEMENT_ENABLED=true."""
from dataclasses import dataclass
from typing import Optional

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings

logger = structlog.get_logger()
bearer_scheme = HTTPBearer(auto_error=False)

SYSTEM_USER_ID = "00000000-0000-0000-0000-000000000001"


@dataclass
class CurrentUser:
    user_id: str
    is_system: bool = False


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> CurrentUser:
    if not settings.auth_enforcement_enabled:
        return CurrentUser(user_id=SYSTEM_USER_ID, is_system=True)

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
        )

    try:
        from jose import JWTError, jwt

        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise ValueError("Missing sub claim")
        return CurrentUser(user_id=user_id)
    except (JWTError, ValueError) as exc:
        logger.warning("jwt_validation_failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc
