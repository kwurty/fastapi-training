"""implementing user table

Revision ID: d5a48d78767b
Revises: 29cf8ffffc05
Create Date: 2022-02-28 20:45:35.184367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5a48d78767b'
down_revision = '29cf8ffffc05'
branch_labels = None
depends_on = None


def upgrade():

    # Create the users table
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email'))
    pass


def downgrade():
    op.drop_table('users')
    pass
