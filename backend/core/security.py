from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from backend.core.config import get_supabase_anon

security = HTTPBearer()


class User(BaseModel):
    id: str
    email: str
    role: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials

    try:
        supabase = get_supabase_anon()

        # ✅ Let Supabase validate the JWT
        response = supabase.auth.get_user(token)

        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")

        user = response.user
        role = user.user_metadata.get("role", "user")

        return User(
            id=user.id,
            email=user.email,
            role=role,
        )

    except HTTPException:
        raise

    except Exception as e:
        print("AUTH ERROR:", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
