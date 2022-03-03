"""adding username field to users table

Revision ID: afd691941bd1
Revises: 4d37a69358c1
Create Date: 2022-03-02 16:37:37.252533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afd691941bd1'
down_revision = '4d37a69358c1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('username', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('users', 'username')
    pass
