"""check_override_schema_version

Revision ID: b296349fd17b
Revises: 479219fa5c98
Create Date: 2018-07-19 13:24:29.335055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b296349fd17b'
down_revision = '479219fa5c98'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index('ix_release_check_release_id', 'release_check')
    op.drop_index('ix_record_check_record_id', 'record_check')
    op.drop_index('ix_release_check_error_release_id', 'release_check_error')
    op.drop_index('ix_record_check_error_record_id', 'record_check_error')

    op.add_column("release_check",
                  sa.Column('override_schema_version', sa.Text, nullable=True)
                  )
    op.add_column("record_check",
                  sa.Column('override_schema_version', sa.Text, nullable=True)
                  )
    op.add_column("release_check_error",
                  sa.Column('override_schema_version', sa.Text, nullable=True)
                  )
    op.add_column("record_check_error",
                  sa.Column('override_schema_version', sa.Text, nullable=True)
                  )

    op.create_unique_constraint('ix_release_check_release_id_and_more', 'release_check',
                                ['release_id', 'override_schema_version'])
    op.create_unique_constraint('ix_record_check_record_id_and_more', 'record_check',
                                ['record_id', 'override_schema_version'])
    op.create_unique_constraint('ix_release_check_error_release_id_and_more', 'release_check_error',
                                ['release_id', 'override_schema_version'])
    op.create_unique_constraint('ix_record_check_error_record_id_and_more', 'record_check_error',
                                ['record_id', 'override_schema_version'])


def downgrade():
    raise RuntimeError("We can't go back as issues with unique indexes")
