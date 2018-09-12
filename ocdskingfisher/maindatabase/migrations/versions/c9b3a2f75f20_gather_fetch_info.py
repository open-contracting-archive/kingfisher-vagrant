"""gather_fetch_info

Revision ID: c9b3a2f75f20
Revises: 51e747af4522
Create Date: 2018-09-12 15:32:56.683032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9b3a2f75f20'
down_revision = '51e747af4522'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("collection",
                  sa.Column('gather_start_at', sa.DateTime(timezone=False), nullable=True)
                  )
    op.add_column("collection",
                  sa.Column('gather_end_at', sa.DateTime(timezone=False), nullable=True)
                  )
    op.add_column("collection",
                  sa.Column('fetch_start_at', sa.DateTime(timezone=False), nullable=True)
                  )
    op.add_column("collection",
                  sa.Column('fetch_end_at', sa.DateTime(timezone=False), nullable=True)
                  )


def downgrade():
    op.drop_column("collection", 'gather_start_at')
    op.drop_column("collection", 'gather_end_at')
    op.drop_column("collection", 'fetch_start_at')
    op.drop_column("collection", 'fetch_end_at')
