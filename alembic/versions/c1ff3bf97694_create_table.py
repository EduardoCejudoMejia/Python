"""create table

Revision ID: c1ff3bf97694
Revises:
Create Date: 2026-08-11 18:48:49.162766

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "c1ff3bf97694"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
