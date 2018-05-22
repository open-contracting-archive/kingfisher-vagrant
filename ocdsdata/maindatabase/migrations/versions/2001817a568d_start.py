"""start

Revision ID: 2001817a568d
Revises:
Create Date: 2018-05-15 13:27:35.420841

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '2001817a568d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('source_session',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('source_id', sa.Text, nullable=False),
                    sa.Column('data_version', sa.Text, nullable=False),
                    sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=False),
                    sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                    sa.Column('sample', sa.Boolean, nullable=False, default=False),
                    sa.UniqueConstraint('source_id', 'data_version', 'sample'),
                    )

    op.create_table('source_session_file_status',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('source_session_id', sa.Integer,
                              sa.ForeignKey("source_session.id"), nullable=False),
                    sa.Column('filename', sa.Text, nullable=True),
                    sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=True),
                    sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                    sa.UniqueConstraint('source_session_id', 'filename'),
                    )

    op.create_table('data',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                    sa.Column('data', JSONB, nullable=False),
                    )

    op.create_table('package_data',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                    sa.Column('data', JSONB, nullable=False),
                    )

    op.create_table('release',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('source_session_file_status_id', sa.Integer,
                              sa.ForeignKey("source_session_file_status.id"), nullable=False),
                    sa.Column('release_id', sa.Text, nullable=True),
                    sa.Column('ocid', sa.Text, nullable=True),
                    sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                    sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                    )

    op.create_table('record',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('source_session_file_status_id', sa.Integer,
                              sa.ForeignKey("source_session_file_status.id"), nullable=False),
                    sa.Column('ocid', sa.Text, nullable=True),
                    sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                    sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"), nullable=False),
                    )

    op.create_table('release_check',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                              unique=True),
                    sa.Column('cove_output', JSONB, nullable=False)
                    )

    op.create_table('record_check',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True,
                              unique=True),
                    sa.Column('cove_output', JSONB, nullable=False)
                    )


def downgrade():
    op.drop_table('record_check')
    op.drop_table('release_check')
    op.drop_table('record')
    op.drop_table('release')
    op.drop_table('package_data')
    op.drop_table('data')
    op.drop_table('source_session_file_status')
    op.drop_table('source_session')
