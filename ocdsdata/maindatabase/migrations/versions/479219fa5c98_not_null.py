"""not-null

Revision ID: 479219fa5c98
Revises: b3d152ef7779
Create Date: 2018-07-18 13:47:25.390348

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '479219fa5c98'
down_revision = 'b3d152ef7779'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('release_check', 'release_id', nullable=False)
    op.alter_column('record_check', 'record_id', nullable=False)


def downgrade():
    op.alter_column('release_check', 'release_id', nullable=True)
    op.alter_column('record_check', 'record_id', nullable=True)
