"""create user table

Revision ID: 8cafc01efb2e
Revises: 
Create Date: 2022-02-14 13:06:53.296130

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text


# revision identifiers, used by Alembic.
revision = "8cafc01efb2e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("NOW()"),
        ),
    )
    pass


def downgrade():
    op.drop_table("users")
    pass
