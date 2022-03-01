"""add published to posts table

Revision ID: 4d37a69358c1
Revises: 929a38b8a0b5
Create Date: 2022-02-28 21:07:25.199312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d37a69358c1'
down_revision = '929a38b8a0b5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('published', sa.Boolean(),
                  server_default='TRUE', nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'published')
    pass
