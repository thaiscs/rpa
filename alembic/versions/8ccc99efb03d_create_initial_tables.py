"""create initial tables

Revision ID: 8ccc99efb03d
Revises: 
Create Date: 2026-04-13 13:16:41.563399

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from shared.triggers import create_updated_at_trigger


# revision identifiers, used by Alembic.
revision: str = '8ccc99efb03d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# --- ENUM -------------------------------------------------------------
person_type_enum = postgresql.ENUM(
    "individual",
    "company",
    "mei",
    "other",
    name="person_type_enum",
    create_type=False,
)


def upgrade():
    """Upgrade schema."""
    
    # ---- ENUM type ------------------------------------------------
    person_type_enum.create(op.get_bind(), checkfirst=True)

    # --- CLIENTS TABLE ------------------------------------------------
    op.create_table(
        "clients",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("legal_name", sa.String(), nullable=False),
        sa.Column("tax_id", sa.String(), nullable=False, unique=True),
        sa.Column(
            "person_type",
            person_type_enum,
            nullable=False,
            server_default=sa.text("'company'"),
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # --- CERTIFICATES TABLE ------------------------------------------
    op.create_table(
        "certificates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "clients.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("encrypted_pfx", postgresql.JSONB(), nullable=False),
        sa.Column("encrypted_pfx_password", postgresql.JSONB(), nullable=False),
        sa.Column("encrypted_cert", postgresql.JSONB(), nullable=False),
        sa.Column("encrypted_key", postgresql.JSONB(), nullable=False),
        sa.Column("issuer", sa.String()),
        sa.Column("valid_from", sa.TIMESTAMP(timezone=True)),
        sa.Column("valid_to", sa.TIMESTAMP(timezone=True)),
        sa.Column("expired", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    # --- TRIGGERS ------------------------------------------
    conn = op.get_bind()
    create_updated_at_trigger(conn)


def downgrade():
    """Downgrade schema."""
    # Drop triggers
    conn = op.get_bind()
    conn.execute(sa.text("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE;"))
    
    # Drop tables
    op.drop_table("certificates")
    op.drop_table("clients")