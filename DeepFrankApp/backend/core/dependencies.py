"""Shared dependencies for FastAPI routes"""
from typing import Optional
from fastapi import HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth_service import AuthService
from services.user_service import UserService
from models.db_models import User
from core.database import get_db

# Global service instances (lazy loaded)
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """
    Get or initialize the authentication service
    
    Returns:
        AuthService instance
        
    Raises:
        HTTPException: If Stytch configuration is missing
    """
    global _auth_service
    
    if _auth_service is None:
        try:
            _auth_service = AuthService()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize auth service: {str(e)}"
            )
    
    return _auth_service


async def get_database() -> AsyncSession:
    """Get database session"""
    async for session in get_db():
        yield session


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user from session token
    
    This dependency requires authentication. Use in routes that need a logged-in user.
    
    Args:
        authorization: Authorization header containing "Bearer <token>"
        db: Database session
        auth_service: Auth service instance
        
    Returns:
        User database model
        
    Raises:
        HTTPException: If token is invalid, missing, or user not found
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authorization scheme")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>"
        )
    
    # Validate session with Stytch
    try:
        session_data = auth_service.get_user_from_session(token)
        stytch_user_id = session_data["stytch_user_id"]
        emails = session_data["user"]["emails"]
        
        if not emails:
            raise HTTPException(
                status_code=401,
                detail="User email not found in session"
            )
        
        email = emails[0]
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired session: {str(e)}"
        )
    
    # Get or create user in database using service
    user = await UserService.get_or_create_user(db, stytch_user_id, email)
    
    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_database),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Dependency to optionally get current authenticated user from session token
    
    This dependency does NOT require authentication. Returns None if no valid token is provided.
    Use in routes that work with or without authentication.
    
    Args:
        authorization: Authorization header containing "Bearer <token>" (optional)
        db: Database session
        auth_service: Auth service instance
        
    Returns:
        User database model if authenticated, None otherwise
    """
    if not authorization:
        print("get_optional_user: No authorization header provided")
        return None
    
    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            print(f"get_optional_user: Invalid authorization scheme: {scheme}")
            return None
        print(f"get_optional_user: Token extracted (first 10 chars: {token[:10]}...)")
    except ValueError as e:
        print(f"get_optional_user: Error parsing authorization header: {e}")
        return None
    
    # Validate session with Stytch
    try:
        session_data = auth_service.get_user_from_session(token)
        stytch_user_id = session_data["stytch_user_id"]
        emails = session_data["user"]["emails"]
        
        if not emails:
            print("get_optional_user: No emails found in session data")
            return None
        
        email = emails[0]
        print(f"get_optional_user: Session validated for user: {email}")
    except (ValueError, Exception) as e:
        print(f"get_optional_user: Error validating session: {e}")
        return None
    
    # Get or create user in database using service
    try:
        user = await UserService.get_or_create_user(db, stytch_user_id, email)
        return user
    except Exception as e:
        print(f"get_optional_user: Error getting/creating user in database: {e}")
        return None

