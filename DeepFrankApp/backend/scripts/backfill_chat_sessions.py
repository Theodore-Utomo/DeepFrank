"""
Backfill script to link existing ImageAnalysis records to their ChatSessions.

This script:
1. Finds all ImageAnalysis records without chat_session_id
2. For each, tries to find a matching ChatSession by:
   - Same user_id
   - Created within a time window (default 5 minutes)
   - First message content matches the analysis_text
3. Links them together
"""
import asyncio
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from core.database import get_db
from models.db_models import ImageAnalysis, ChatSession, ChatMessage


async def backfill_chat_sessions(
    db: AsyncSession,
    time_window_minutes: int = 5,
    dry_run: bool = True
) -> dict:
    """
    Backfill chat_session_id for existing ImageAnalysis records.
    
    Args:
        db: Database session
        time_window_minutes: Time window to match analyses and sessions (default 5 minutes)
        dry_run: If True, only report what would be done without making changes
        
    Returns:
        Dictionary with statistics about the backfill operation
    """
    stats = {
        'total_analyses': 0,
        'analyses_without_chat': 0,
        'matched': 0,
        'not_matched': 0,
        'errors': 0
    }
    
    # Find all analyses without chat_session_id
    result = await db.execute(
        select(ImageAnalysis)
        .where(ImageAnalysis.chat_session_id.is_(None))
        .where(ImageAnalysis.user_id.isnot(None))  # Only for authenticated users
        .order_by(ImageAnalysis.created_at.desc())
    )
    analyses = result.scalars().all()
    
    stats['total_analyses'] = len(analyses)
    stats['analyses_without_chat'] = len(analyses)
    
    print(f"Found {len(analyses)} analyses without chat_session_id")
    
    for analysis in analyses:
        try:
            if not analysis.user_id:
                continue
                
            if not analysis.analysis_result:
                print(f"  Skipping analysis {analysis.id}: no analysis_result")
                continue
            
            # Find potential matching chat sessions
            # Match by: same user_id, created within time window, first message matches analysis_text
            time_window_start = analysis.created_at - timedelta(minutes=time_window_minutes)
            time_window_end = analysis.created_at + timedelta(minutes=time_window_minutes)
            
            # Find chat sessions for this user within the time window
            session_result = await db.execute(
                select(ChatSession)
                .where(
                    and_(
                        ChatSession.user_id == analysis.user_id,
                        ChatSession.created_at >= time_window_start,
                        ChatSession.created_at <= time_window_end
                    )
                )
                .order_by(ChatSession.created_at.asc())
            )
            potential_sessions = session_result.scalars().all()
            
            matched_session = None
            
            # For each potential session, check if first message matches analysis_text
            for session in potential_sessions:
                # Get first message in this session
                first_message_result = await db.execute(
                    select(ChatMessage)
                    .where(ChatMessage.session_id == session.id)
                    .where(ChatMessage.sender == 'assistant')
                    .order_by(ChatMessage.created_at.asc())
                    .limit(1)
                )
                first_message = first_message_result.scalar_one_or_none()
                
                if first_message:
                    # Check if content matches (allowing for some variation)
                    analysis_text_clean = analysis.analysis_result.strip()
                    message_content_clean = first_message.content.strip()
                    
                    # Exact match or analysis text is contained in message
                    if (analysis_text_clean == message_content_clean or 
                        analysis_text_clean in message_content_clean or
                        message_content_clean in analysis_text_clean):
                        matched_session = session
                        break
            
            if matched_session:
                if not dry_run:
                    analysis.chat_session_id = matched_session.id
                    await db.commit()
                    await db.refresh(analysis)
                print(f"  ✓ Matched analysis {analysis.id} to session {matched_session.id}")
                stats['matched'] += 1
            else:
                print(f"  ✗ No match found for analysis {analysis.id} (user: {analysis.user_id}, created: {analysis.created_at})")
                stats['not_matched'] += 1
                
        except Exception as e:
            print(f"  ✗ Error processing analysis {analysis.id}: {e}")
            stats['errors'] += 1
    
    return stats


async def main():
    """Main entry point for the backfill script"""
    import sys
    
    dry_run = '--execute' not in sys.argv
    
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No changes will be made")
        print("Add --execute flag to actually update the database")
        print("=" * 60)
    else:
        print("=" * 60)
        print("EXECUTION MODE - Changes will be saved to database")
        print("=" * 60)
    
    async for db in get_db():
        try:
            stats = await backfill_chat_sessions(db, time_window_minutes=5, dry_run=dry_run)
            
            print("\n" + "=" * 60)
            print("BACKFILL SUMMARY")
            print("=" * 60)
            print(f"Total analyses without chat_session_id: {stats['analyses_without_chat']}")
            print(f"Successfully matched: {stats['matched']}")
            print(f"Not matched: {stats['not_matched']}")
            print(f"Errors: {stats['errors']}")
            print("=" * 60)
            
        finally:
            await db.close()
            break  # Exit after first session


if __name__ == "__main__":
    asyncio.run(main())

