"""Authentication routes using Stytch"""
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from models.schemas import (
    MagicLinkRequest,
    MagicLinkAuthenticateRequest,
    MagicLinkSendResponse,
    AuthResponse,
    SessionResponse,
    LogoutResponse
)
from models.db_models import User
from services.auth_service import AuthService
from core.dependencies import get_database, get_auth_service, get_current_user

router = APIRouter()


@router.post("/auth/magic-link/send", response_model=MagicLinkSendResponse)
async def send_magic_link(
    request: MagicLinkRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Send magic link email to user
    
    Request body:
    - email: User's email address
    """
    try:
        result = auth_service.send_magic_link(request.email)
        return MagicLinkSendResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send magic link: {str(e)}")


@router.post("/auth/magic-link/authenticate", response_model=AuthResponse)
async def authenticate_magic_link(
    request: MagicLinkAuthenticateRequest,
    db: AsyncSession = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate magic link token and create/update user session
    
    Request body:
    - token: Magic link token from email
    """
    try:
        return await auth_service.authenticate_and_get_user(db, request.token)
    except ValueError as e:
        # Check if it's an expired/used link error
        error_msg = str(e)
        if 'already used' in error_msg or 'expired' in error_msg:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the full error for debugging
        print(f"Authentication error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to authenticate: {str(e)}")


@router.get("/auth/me", response_model=SessionResponse)
async def get_current_user_info(
    user: User = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current authenticated user information
    """
    try:
        token = auth_service.extract_token_from_header(authorization)
        return auth_service.get_user_session_info(user, token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by revoking session token
    """
    try:
        token = auth_service.extract_token_from_header(authorization)
        result = auth_service.revoke_session(token)
        return LogoutResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to logout: {str(e)}")

