"""add_chat_session_id_to_image_analyses

Revision ID: 2846b90449fa
Revises: fcbe3410f9a5
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2846b90449fa'
down_revision: Union[str, None] = 'fcbe3410f9a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add chat_session_id column to image_analyses table
    op.add_column(
        'image_analyses',
        sa.Column(
            'chat_session_id',
            postgresql.UUID(as_uuid=True),
            nullable=True
        )
    )
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_image_analyses_chat_session_id',
        'image_analyses',
        'chat_sessions',
        ['chat_session_id'],
        ['id']
    )
    # Add index for better query performance
    op.create_index(
        'ix_image_analyses_chat_session_id',
        'image_analyses',
        ['chat_session_id'],
        unique=False
    )


def downgrade() -> None:
    # Drop index
    op.drop_index('ix_image_analyses_chat_session_id', table_name='image_analyses')
    # Drop foreign key constraint
    op.drop_constraint('fk_image_analyses_chat_session_id', 'image_analyses', type_='foreignkey')
    # Drop column
    op.drop_column('image_analyses', 'chat_session_id')

