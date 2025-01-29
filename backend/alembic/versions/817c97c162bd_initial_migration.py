"""initial_migration

Revision ID: 817c97c162bd
Revises: 20240129_users
Create Date: 2025-01-29 17:26:05.586078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '817c97c162bd'
down_revision: Union[str, None] = '20240129_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
