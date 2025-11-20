"""User service for database operations"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.db_models import User


class UserService:
    """Service for user database operations"""
    
    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        stytch_user_id: str,
        email: str
    ) -> User:
        """
        Get existing user or create a new one
        
        Args:
            db: Database session
            stytch_user_id: Stytch user identifier
            email: User email address
            
        Returns:
            User database model
        """
        # Try to find existing user
        result = await db.execute(
            select(User).where(User.stytch_user_id == stytch_user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                stytch_user_id=stytch_user_id,
                email=email
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"UserService: Created new user with id: {user.id}")
        elif user.email != email:
            # Update email if it changed
            user.email = email
            await db.commit()
            await db.refresh(user)
            print(f"UserService: Updated user email, user id: {user.id}")
        else:
            print(f"UserService: Found existing user with id: {user.id}")
        
        return user
    
    @staticmethod
    async def get_user_by_stytch_id(
        db: AsyncSession,
        stytch_user_id: str
    ) -> Optional[User]:
        """
        Get user by Stytch user ID
        
        Args:
            db: Database session
            stytch_user_id: Stytch user identifier
            
        Returns:
            User database model or None if not found
        """
        result = await db.execute(
            select(User).where(User.stytch_user_id == stytch_user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            User database model or None if not found
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

