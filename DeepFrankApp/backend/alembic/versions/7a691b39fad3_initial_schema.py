"""Initial schema

Revision ID: 7a691b39fad3
Revises: 
Create Date: 2025-11-12 05:13:00.271953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a691b39fad3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('stytch_user_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_stytch_user_id', 'users', ['stytch_user_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    # Create image_analyses table
    op.create_table(
        'image_analyses',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('detections', sa.dialects.postgresql.JSON(), nullable=True),
        sa.Column('analysis_result', sa.Text(), nullable=True),
        sa.Column('emotion', sa.String(), nullable=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index('ix_image_analyses_id', 'image_analyses', ['id'], unique=False)
    op.create_index('ix_image_analyses_user_id', 'image_analyses', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_image_analyses_user_id', table_name='image_analyses')
    op.drop_index('ix_image_analyses_id', table_name='image_analyses')
    op.drop_table('image_analyses')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_stytch_user_id', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
