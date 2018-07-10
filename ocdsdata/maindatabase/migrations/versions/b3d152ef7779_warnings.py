"""warnings

Revision ID: b3d152ef7779
Revises: 1cf223a50773
Create Date: 2018-07-10 14:16:55.315274

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'b3d152ef7779'
down_revision = '1cf223a50773'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("source_session_file_status",
                  sa.Column('warnings', JSONB, nullable=True)
                  )


def downgrade():
    op.drop_column("source_session_file_status", 'fetch_warnings')
