"""empty message

Revision ID: 68d4146317ff
Revises: 62907e76d6c8
Create Date: 2017-11-10 14:51:24.035278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68d4146317ff'
down_revision = '62907e76d6c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('smstpls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('smstpls')
    # ### end Alembic commands ###
