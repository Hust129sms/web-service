"""empty message

Revision ID: d82f61d1099b
Revises: 35fe27f16cfc
Create Date: 2018-01-07 20:03:25.859769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd82f61d1099b'
down_revision = '35fe27f16cfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group_members', sa.Column('data_backup', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group_members', 'data_backup')
    # ### end Alembic commands ###
