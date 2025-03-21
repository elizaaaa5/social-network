"""empty message

Revision ID: 503322a07d2f
Revises: 
Create Date: 2025-03-21 21:34:49.020109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '503322a07d2f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.String, primary_key=True, index=True),
        sa.Column('login', sa.String, unique=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('password_hash', sa.String),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
        sa.Column('phone_number', sa.String),
        sa.Column('birth_date', sa.Date),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
