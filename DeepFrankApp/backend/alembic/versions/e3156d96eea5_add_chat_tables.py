"""add_chat_tables

Revision ID: e3156d96eea5
Revises: 7a691b39fad3
Create Date: 2025-11-13 20:24:56.467065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3156d96eea5'
down_revision: Union[str, None] = '7a691b39fad3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index('ix_chat_sessions_id', 'chat_sessions', ['id'], unique=False)
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'], unique=False)
    
    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
    )
    op.create_index('ix_chat_messages_id', 'chat_messages', ['id'], unique=False)
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_chat_messages_session_id', table_name='chat_messages')
    op.drop_index('ix_chat_messages_id', table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index('ix_chat_sessions_user_id', table_name='chat_sessions')
    op.drop_index('ix_chat_sessions_id', table_name='chat_sessions')
    op.drop_table('chat_sessions')
