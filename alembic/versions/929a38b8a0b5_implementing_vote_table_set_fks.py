"""implementing vote table - set fks

Revision ID: 929a38b8a0b5
Revises: d5a48d78767b
Create Date: 2022-02-28 20:59:20.707843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '929a38b8a0b5'
down_revision = 'd5a48d78767b'
branch_labels = None
depends_on = None


def upgrade():
    # op.add_column('posts', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table="posts", referent_table="users", local_cols=[
                          'user_id'], remote_cols=['id'], ondelete="CASCADE")

    op.create_table('votes',
                    sa.Column('user_id', sa.Integer(),
                              nullable=False, primary_key=True),
                    sa.Column('post_id', sa.Integer(), nullable=False, primary_key=True))

    op.create_foreign_key('vote_user_fk', source_table="votes", referent_table="users", local_cols=[
                          'user_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('vote_post_fk', source_table="votes", referent_table="posts", local_cols=[
                          'post_id'], remote_cols=['id'], ondelete="CASCADE")
    pass


def downgrade():
    op.drop_constraint('post_users_fk')
    op.drop_constraint('vote_user_fk')
    op.drop_constraint('vote_post_fk')
    op.drop_table('votes')
    pass
