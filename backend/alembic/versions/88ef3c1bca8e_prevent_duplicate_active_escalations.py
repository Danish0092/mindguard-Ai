
"""prevent duplicate active escalations

Revision ID: 88ef3c1bca8e
Revises: fbd05ea3cfd0
"""

from alembic import op
import sqlalchemy as sa

revision = "88ef3c1bca8e"
down_revision = "fbd05ea3cfd0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_escalations_one_active_per_student",
        "escalations",
        ["student_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('OPEN', 'ACKNOWLEDGED')"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_escalations_one_active_per_student",
        table_name="escalations",
    )
