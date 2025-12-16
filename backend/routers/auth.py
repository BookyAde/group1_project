from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from supabase import Client, AuthError # Import Client and AuthError for better error handling

# 1. IMPORT GETTER FUNCTIONS
from backend.core.config import get_supabase_anon, get_supabase_service 
from backend.core.security import get_current_user, get_admin_user, User

router = APIRouter(prefix="/auth", tags=["Auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


# 2. DEFINE DEPENDENCY FUNCTIONS
def get_anon_client() -> Client:
    return get_supabase_anon()

def get_service_client() -> Client:
    return get_supabase_service()


@router.post("/signup")
async def signup(
    credentials: SignupRequest,
    # 3. Inject the service client using Depends()
    supabase_service: Client = Depends(get_service_client)
):
    """Sign up a new user"""
    try:
        response = supabase_service.auth.sign_up(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        return {
            "message": "Signup successful! Check your email for verification.",
            "user": response.user.email if response.user else None,
        }

    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {e.message}",
        )
    except Exception as e:
        # Catch other errors, like initialization error if Depends failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.post("/login")
async def login(
    credentials: LoginRequest,
    # 3. Inject the anon client using Depends()
    supabase_anon: Client = Depends(get_anon_client)
):
    """Login a user"""
    try:
        response = supabase_anon.auth.sign_in_with_password(
            {
                "email": credentials.email,
                "password": credentials.password,
            }
        )

        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
        }

    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.post("/verify")
async def verify_email(
    request: VerifyRequest,
    # 3. Inject the anon client using Depends()
    supabase_anon: Client = Depends(get_anon_client)
):
    """Verify email with OTP code"""
    try:
        response = supabase_anon.auth.verify_otp(
            {
                "email": request.email,
                "token": request.code,
                "type": "email",
            }
        )

        return {
            "message": "Email verified successfully",
            "access_token": response.session.access_token,
            "user": {"email": response.user.email},
        }

    except AuthError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification failed",
        )


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }