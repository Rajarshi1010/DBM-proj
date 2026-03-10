"""merge_conflicts

Revision ID: c77d9753b554
Revises: 162097906645, 570037feb054
Create Date: 2025-12-14 12:11:26.804385

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c77d9753b554'
down_revision: Union[str, Sequence[str], None] = ('162097906645', '570037feb054')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
