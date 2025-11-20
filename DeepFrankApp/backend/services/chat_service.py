"""Chat service for business logic operations"""
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_ollama import ChatOllama
from langgraph.graph import add_messages
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TEMPERATURE, CHAT_SYSTEM_PROMPT
from models.db_models import ChatSession, ChatMessage
from models.schemas import ChatSessionResponse, ChatMessageRequest, ChatMessageResponse


# Initialize Ollama LLM
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=OLLAMA_TEMPERATURE
)

# Initialize checkpointer for conversation state
checkpointer = InMemorySaver()


@task
def call_model(messages: List[BaseMessage]):
    """Call the Ollama model with messages"""
    response = llm.invoke(messages)
    return response


@entrypoint(checkpointer=checkpointer)
def workflow(inputs: List[BaseMessage], *, previous: List[BaseMessage] = None):
    """
    LangGraph workflow for chat conversations
    
    Args:
        inputs: Messages to process (should include full conversation history from database)
        previous: Previous conversation messages (from checkpointer, may be None)
    
    Returns:
        AI response message
    """
    # Check if inputs already include system prompt (first message should be SystemMessage)
    has_system_prompt = inputs and isinstance(inputs[0], SystemMessage)
    
    # If we have previous state from checkpointer, merge it
    # Otherwise use inputs as-is (they should already include full history from database)
    if previous:
        # Merge previous state with new inputs
        all_messages = add_messages(previous, inputs)
    else:
        # No previous state - use inputs directly
        all_messages = inputs
        # Add system prompt if not already present
        if not has_system_prompt:
            system_message = SystemMessage(content=CHAT_SYSTEM_PROMPT)
            all_messages = add_messages([system_message], all_messages)
    
    response = call_model(all_messages).result()
    return entrypoint.final(value=response, save=add_messages(all_messages, response))


class ChatService:
    """Service for chat business logic operations"""

    @staticmethod
    async def create_session(
        user_id: UUID,
        db: AsyncSession
    ) -> ChatSession:
        """
        Create a new chat session
        
        Args:
            user_id: User UUID
            db: Database session
            
        Returns:
            Created ChatSession
        """
        session = ChatSession(user_id=user_id)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_session(
        session_id: UUID,
        db: AsyncSession
    ) -> ChatSession:
        """
        Get a chat session by ID
        
        Args:
            session_id: Session UUID
            db: Database session
            
        Returns:
            ChatSession if found
            
        Raises:
            HTTPException: If session not found
        """
        session = await db.get(ChatSession, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @staticmethod
    async def get_session_messages(
        session_id: UUID,
        db: AsyncSession
    ) -> List[ChatMessage]:
        """
        Get all messages for a chat session
        
        Args:
            session_id: Session UUID
            db: Database session
            
        Returns:
            List of ChatMessage records ordered by creation time
        """
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def save_message(
        session_id: UUID,
        sender: str,
        content: str,
        db: AsyncSession
    ) -> ChatMessage:
        """
        Save a chat message to the database
        
        Args:
            session_id: Session UUID
            sender: Message sender ("user" or "assistant")
            content: Message content
            db: Database session
            
        Returns:
            Saved ChatMessage
        """
        message = ChatMessage(
            session_id=session_id,
            sender=sender,
            content=content
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    def _convert_db_messages_to_langchain(
        db_messages: List[ChatMessage]
    ) -> List[BaseMessage]:
        """
        Convert database messages to LangChain message format
        
        Args:
            db_messages: List of ChatMessage from database
            
        Returns:
            List of LangChain BaseMessage objects
        """
        langchain_messages = []
        for msg in db_messages:
            if msg.sender == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.sender == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        return langchain_messages

    @staticmethod
    async def send_message(
        message_request: ChatMessageRequest,
        user_id: UUID,
        db: AsyncSession
    ) -> ChatMessageResponse:
        """
        Send a chat message and get AI response
        
        This is the main business logic for chat interactions.
        
        Args:
            message_request: Chat message request
            user_id: User UUID
            db: Database session
            
        Returns:
            AI response message
            
        Raises:
            HTTPException: If session not found or user doesn't own session
        """
        # Verify session exists and belongs to user
        session = await ChatService.get_session(message_request.session_id, db)
        if session.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this chat session"
            )
        
        # Save user message to database
        user_message = await ChatService.save_message(
            session_id=message_request.session_id,
            sender="user",
            content=message_request.content,
            db=db
        )
        
        # Get conversation history from database (excluding the message we just added)
        db_messages = await ChatService.get_session_messages(
            message_request.session_id,
            db
        )
        
        # Convert previous messages to LangChain format (exclude the user message we just added)
        previous_messages = ChatService._convert_db_messages_to_langchain(
            [msg for msg in db_messages if msg.id != user_message.id]
        )
        
        # Create user message for LangChain
        user_langchain_message = HumanMessage(content=message_request.content)
        
        # Get AI response using LangGraph workflow
        # Use session_id as thread_id for conversation continuity
        config = {"configurable": {"thread_id": str(message_request.session_id)}}
        
        try:
            # Build full conversation history for the workflow
            # Since InMemorySaver is in-memory only, we load from database each time
            # and pass the full conversation to the workflow
            if previous_messages:
                # We have previous messages - include system prompt and full history
                all_messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)] + previous_messages + [user_langchain_message]
            else:
                # First message - workflow will add system prompt if needed
                all_messages = [user_langchain_message]
            
            # Get AI response using invoke
            # Pass full conversation history so workflow has context
            response = workflow.invoke(all_messages, config)
            
            # Extract content from response
            if hasattr(response, 'content'):
                ai_response_content = response.content
            elif isinstance(response, dict) and 'value' in response:
                message = response['value']
                if hasattr(message, 'content'):
                    ai_response_content = message.content
                else:
                    ai_response_content = str(message)
            else:
                ai_response_content = str(response)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get AI response: {str(e)}"
            )
        
        # Save AI response to database
        ai_message = await ChatService.save_message(
            session_id=message_request.session_id,
            sender="assistant",
            content=ai_response_content,
            db=db
        )
        
        # Return AI response
        return ChatMessageResponse(
            id=str(ai_message.id),
            session_id=str(ai_message.session_id),
            sender=ai_message.sender,
            content=ai_message.content,
            created_at=ai_message.created_at.isoformat() if ai_message.created_at else "",
            updated_at=ai_message.updated_at.isoformat() if ai_message.updated_at else ""
        )
