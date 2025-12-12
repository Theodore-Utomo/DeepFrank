"""Authentication service using Stytch"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from stytch import Client
from stytch.core.response_base import StytchError
from core.config import STYTCH_PROJECT_ID, STYTCH_SECRET, STYTCH_ENVIRONMENT, MAGIC_LINK_REDIRECT_URL
from services.user_service import UserService
from models.schemas import AuthResponse, UserResponse, SessionResponse
from models.db_models import User


class AuthService:
    """Service for handling authentication via Stytch"""
    
    def __init__(self):
        """Initialize Stytch client"""
        if not STYTCH_PROJECT_ID or not STYTCH_SECRET:
            raise ValueError("STYTCH_PROJECT_ID and STYTCH_SECRET must be set in environment variables")
        
        self.client = Client(
            project_id=STYTCH_PROJECT_ID,
            secret=STYTCH_SECRET,
            environment=STYTCH_ENVIRONMENT
        )
    
    def send_magic_link(self, email: str, redirect_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send magic link email to user
        
        Args:
            email: User's email address
            redirect_url: Optional redirect URL after authentication (defaults to config value)
            
        Returns:
            Dictionary with status and message
        """
        try:
            redirect = redirect_url or MAGIC_LINK_REDIRECT_URL
            
            response = self.client.magic_links.email.login_or_create(
                email=email,
                login_magic_link_url=redirect,
                signup_magic_link_url=redirect
            )
            
            return {
                "status": "success",
                "message": "Magic link sent successfully",
                "email_id": response.email_id if hasattr(response, 'email_id') else None
            }
        except StytchError as e:
            # Handle specific Stytch errors with better messages
            error_type = getattr(e, 'error_type', None)
            error_message = getattr(e, 'error_message', str(e))
            
            if error_type == 'inactive_email':
                raise ValueError(
                    f"This email address has been marked as inactive. "
                    f"This usually happens when an email bounces. "
                    f"Please reactivate the email in the Stytch Dashboard or use a different email address. "
                    f"Details: {error_message}"
                )
            elif error_type == 'rate_limit_exceeded':
                raise ValueError(
                    f"Too many requests. Please wait a moment and try again. "
                    f"Details: {error_message}"
                )
            else:
                raise ValueError(f"Failed to send magic link: {error_message}")
        except Exception as e:
            error_str = str(e)
            # Check for DNS/network errors
            if 'Failed to resolve' in error_str or 'NameResolutionError' in error_str:
                raise ValueError(
                    f"Network error: Unable to connect to Stytch service. "
                    f"Please check your internet connection and try again. "
                    f"Details: {error_str}"
                )
            raise ValueError(f"Failed to send magic link: {error_str}")
    
    def authenticate_magic_link(self, token: str) -> Dict[str, Any]:
        """
        Authenticate magic link token and get user session
        
        Args:
            token: Magic link token from email
            
        Returns:
            Dictionary with session_token, user_id, and user info
        """
        try:
            print(f"Attempting to authenticate magic link token: {token[:20]}...")
            print(f"Full token length: {len(token)}")
            print(f"Token starts with: {token[:5]}...")
            
            response = self.client.magic_links.authenticate(
                token=token,
                session_duration_minutes=60 * 24 * 7 
            )
            
            if not response.session_token:
                raise ValueError("No session token returned from Stytch")
            
            print(f"Successfully authenticated magic link for user: {response.user_id}")
            
            emails = []
            if hasattr(response, 'emails') and response.emails:
                emails = [email.email for email in response.emails]
            elif hasattr(response, 'user') and hasattr(response.user, 'emails'):
                emails = [email.email for email in response.user.emails]
            
            # Log response structure for debugging
            print(f"Response has 'emails' attribute: {hasattr(response, 'emails')}")
            if hasattr(response, 'emails'):
                print(f"Response.emails type: {type(response.emails)}")
                print(f"Response.emails value: {response.emails}")
            if hasattr(response, 'user'):
                print(f"Response.user type: {type(response.user)}")
                if hasattr(response.user, 'emails'):
                    print(f"Response.user.emails: {response.user.emails}")
            
            print(f"Extracted emails: {emails}")
            
            return {
                "session_token": response.session_token,
                "stytch_user_id": response.user_id,
                "user": {
                    "user_id": response.user_id,
                    "emails": emails
                }
            }
        except StytchError as e:
            error_type = getattr(e, 'error_type', None)
            error_message = getattr(e, 'error_message', str(e))
            error_str = str(e)
            print(f"Stytch authentication error: {error_str}")
            
            if error_type in ['magic_link_token_not_found', 'magic_link_token_expired', 'magic_link_token_already_used']:
                raise ValueError("This magic link has already been used or has expired. Please request a new one.")
            elif 'invalid' in error_str.lower() or error_type == 'invalid_token':
                raise ValueError("Invalid magic link token. Please request a new magic link.")
            else:
                raise ValueError(f"Failed to authenticate magic link: {error_message}")
        except Exception as e:
            error_str = str(e)
            print(f"Stytch authentication error: {error_str}")
            
            # Check for DNS/network errors
            if 'Failed to resolve' in error_str or 'NameResolutionError' in error_str:
                raise ValueError(
                    f"Network error: Unable to connect to Stytch service. "
                    f"Please check your internet connection and try again. "
                    f"Details: {error_str}"
                )
            
            if 'already used' in error_str or 'expired' in error_str or 'unable_to_auth_magic_link' in error_str:
                raise ValueError("This magic link has already been used or has expired. Please request a new one.")
            elif 'invalid' in error_str.lower():
                raise ValueError("Invalid magic link token. Please request a new magic link.")
            else:
                raise ValueError(f"Failed to authenticate magic link: {error_str}")
    
    def get_user_from_session(self, session_token: str) -> Dict[str, Any]:
        """
        Get user information from Stytch session token
        
        Args:
            session_token: Stytch session token
            
        Returns:
            Dictionary with user_id and user info
        """
        try:
            response = self.client.sessions.authenticate(
                session_token=session_token
            )
            
            # Extract user_id - it might be in response.user_id or response.user.user_id
            user_id = None
            if hasattr(response, 'user_id'):
                user_id = response.user_id
            elif hasattr(response, 'user') and hasattr(response.user, 'user_id'):
                user_id = response.user.user_id
            
            emails = []
            if hasattr(response, 'emails') and response.emails:
                emails = [email.email for email in response.emails]
            elif hasattr(response, 'user') and hasattr(response.user, 'emails') and response.user.emails:
                emails = [email.email for email in response.user.emails]
            
            if not user_id:
                raise ValueError("User ID not found in session response")
            
            return {
                "stytch_user_id": user_id,
                "user": {
                    "user_id": user_id,
                    "emails": emails
                },
                "session": {
                    "session_id": response.session_id if hasattr(response, 'session_id') else None,
                    "expires_at": response.expires_at if hasattr(response, 'expires_at') else None
                }
            }
        except StytchError as e:
            error_type = getattr(e, 'error_type', None)
            error_message = getattr(e, 'error_message', str(e))
            error_str = str(e)
            print(f"get_user_from_session StytchError: {error_str}")
            raise ValueError(f"Failed to authenticate session: {error_message}")
        except Exception as e:
            error_str = str(e)
            print(f"get_user_from_session error: {error_str}")
            print(f"Response type: {type(response) if 'response' in locals() else 'N/A'}")
            if 'response' in locals():
                print(f"Response attributes: {dir(response)}")
            # Check for DNS/network errors
            if 'Failed to resolve' in error_str or 'NameResolutionError' in error_str:
                raise ValueError(
                    f"Network error: Unable to connect to Stytch service. "
                    f"Please check your internet connection and try again. "
                    f"Details: {error_str}"
                )
            raise ValueError(f"Failed to authenticate session: {error_str}")
    
    def revoke_session(self, session_token: str) -> Dict[str, Any]:
        """
        Revoke/end a user session (logout)
        
        Args:
            session_token: Stytch session token to revoke
            
        Returns:
            Dictionary with status
        """
        try:
            self.client.sessions.revoke(session_token=session_token)
            return {
                "status": "success",
                "message": "Session revoked successfully"
            }
        except StytchError as e:
            error_message = getattr(e, 'error_message', str(e))
            raise ValueError(f"Failed to revoke session: {error_message}")
        except Exception as e:
            error_str = str(e)
            # Check for DNS/network errors
            if 'Failed to resolve' in error_str or 'NameResolutionError' in error_str:
                raise ValueError(
                    f"Network error: Unable to connect to Stytch service. "
                    f"Please check your internet connection and try again. "
                    f"Details: {error_str}"
                )
            raise ValueError(f"Failed to revoke session: {error_str}")
    
    async def authenticate_and_get_user(
        self,
        db: AsyncSession,
        token: str
    ) -> AuthResponse:
        """
        Authenticate magic link token and get/create user in database
        
        This is the main business logic for magic link authentication.
        
        Args:
            db: Database session
            token: Magic link token from email
            
        Returns:
            AuthResponse with session token and user info
            
        Raises:
            ValueError: If authentication fails or email not found
        """
        print(f"Received authentication request with token length: {len(token)}")
        
        auth_data = self.authenticate_magic_link(token)
        stytch_user_id = auth_data["stytch_user_id"]
        emails = auth_data["user"]["emails"]
        
        print(f"Auth data received - stytch_user_id: {stytch_user_id}, emails: {emails}")
        
        # If no email in response, try to get it from session lookup
        if not emails or len(emails) == 0:
            print("No emails in auth response, attempting to get user info from Stytch...")
            try:
                session_data = self.get_user_from_session(auth_data["session_token"])
                emails = session_data.get("user", {}).get("emails", [])
                print(f"Emails from session lookup: {emails}")
            except Exception as e:
                print(f"Failed to get user info from session: {e}")
            
            if not emails or len(emails) == 0:
                raise ValueError("User email not found in authentication response")
        
        email = emails[0]
        
        user = await UserService.get_or_create_user(db, stytch_user_id, email)
        
        return AuthResponse(
            session_token=auth_data["session_token"],
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                stytch_user_id=user.stytch_user_id,
                created_at=user.created_at.isoformat() if user.created_at else None
            )
        )
    
    def get_user_session_info(
        self,
        user: User,
        session_token: str
    ) -> SessionResponse:
        """
        Get current user session information
        
        Args:
            user: User database model
            session_token: Stytch session token
            
        Returns:
            SessionResponse with user and session info
        """
        session_data = self.get_user_from_session(session_token)
        
        return SessionResponse(
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                stytch_user_id=user.stytch_user_id,
                created_at=user.created_at.isoformat() if user.created_at else None
            ),
            session_id=session_data.get("session", {}).get("session_id"),
            expires_at=session_data.get("session", {}).get("expires_at")
        )
    
    @staticmethod
    def extract_token_from_header(authorization: Optional[str]) -> str:
        """
        Extract Bearer token from Authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            Extracted token string
            
        Raises:
            ValueError: If header is missing or invalid
        """
        if not authorization:
            raise ValueError("Authorization header missing")
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
            return token
        except ValueError as e:
            raise ValueError(f"Invalid authorization header format. Expected: Bearer <token> - {str(e)}")

