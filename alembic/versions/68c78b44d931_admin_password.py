"""admin_password

Revision ID: 68c78b44d931
Revises: 3ae6b06b4b65
Create Date: 2024-02-16 12:36:25.660064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68c78b44d931'
down_revision: Union[str, None] = '3ae6b06b4b65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenant_admins', sa.Column('admin_password', sa.String))


def downgrade() -> None:
    pass
