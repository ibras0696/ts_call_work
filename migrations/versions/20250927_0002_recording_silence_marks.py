from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "20250927_0002"
down_revision = "20250926_0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("recording", sa.Column("silence_marks", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("recording", "silence_marks")
