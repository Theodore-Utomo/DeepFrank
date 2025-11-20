"""rename_role_to_sender

Revision ID: fcbe3410f9a5
Revises: e3156d96eea5
Create Date: 2025-11-13 20:25:48.347920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcbe3410f9a5'
down_revision: Union[str, None] = 'e3156d96eea5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename role column to sender
    op.alter_column('chat_messages', 'role', new_column_name='sender')


def downgrade() -> None:
    # Rename sender column back to role
    op.alter_column('chat_messages', 'sender', new_column_name='role')
