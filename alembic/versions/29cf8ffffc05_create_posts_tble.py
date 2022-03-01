"""
create posts tble

Revision ID: 29cf8ffffc05
Revises: 
Create Date: 2022-02-28 20:34:46.071378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29cf8ffffc05'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("posts",
                    sa.Column('id', sa.Integer(),
                              nullable=False, primary_key=True),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('content', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_table('posts')
    pass
