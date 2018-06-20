"""check-error

Revision ID: 1cf223a50773
Revises: 2001817a568d
Create Date: 2018-06-19 15:32:34.200076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cf223a50773'
down_revision = '2001817a568d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('release_check_error',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                              unique=True, nullable=False),
                    sa.Column('error',  sa.Text, nullable=False)
                    )

    op.create_table('record_check_error',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True,
                              unique=True, nullable=False),
                    sa.Column('error', sa.Text, nullable=False)
                    )


def downgrade():
    op.drop_table('release_check_error')
    op.drop_table('record_check_error')
