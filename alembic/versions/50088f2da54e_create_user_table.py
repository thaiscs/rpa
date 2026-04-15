"""create user table

Revision ID: 50088f2da54e
Revises: 8ccc99efb03d
Create Date: 2026-04-14 10:53:13.812860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '50088f2da54e'
down_revision: Union[str, Sequence[str], None] = '8ccc99efb03d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # --- USERS TABLE ------------------------------------------
    op.create_table(
        "users",
        # -----------------------
        # CUSTOM FIELDS ONLY - inheritance from FastAPI Users base table
        # -----------------------
        sa.Column("name", sa.String(255), nullable=True),

        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("clients.id", ondelete="CASCADE"),
            nullable=True,
        ),    
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
