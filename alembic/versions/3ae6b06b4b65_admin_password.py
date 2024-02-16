"""admin_password

Revision ID: 3ae6b06b4b65
Revises: 0c193166c1b7
Create Date: 2024-02-16 12:32:49.129585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ae6b06b4b65'
down_revision: Union[str, None] = '0c193166c1b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
