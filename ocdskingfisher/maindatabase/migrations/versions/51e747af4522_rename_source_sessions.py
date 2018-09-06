"""rename-source-sessions

Revision ID: 51e747af4522
Revises: b296349fd17b
Create Date: 2018-09-06 10:26:26.589013

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '51e747af4522'
down_revision = 'b296349fd17b'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('source_session', 'collection')
    op.rename_table('source_session_file_status', 'collection_file_status')

    op.alter_column('collection_file_status', 'source_session_id', new_column_name='collection_id')
    op.alter_column('release', 'source_session_file_status_id', new_column_name='collection_file_status_id')
    op.alter_column('record', 'source_session_file_status_id', new_column_name='collection_file_status_id')


def downgrade():
    op.alter_column('record', 'collection_file_status_id', new_column_name='source_session_file_status_id')
    op.alter_column('release', 'collection_file_status_id', new_column_name='source_session_file_status_id')
    op.alter_column('collection_file_status', 'collection_id', new_column_name='source_session_id')

    op.rename_table('collection_file_status', 'source_session_file_status')
    op.rename_table('collection', 'source_session')
