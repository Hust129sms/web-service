"""empty message

Revision ID: 8fb46f544f63
Revises: 09a16599f4e3
Create Date: 2018-02-15 19:39:00.789416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fb46f544f63'
down_revision = '09a16599f4e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group_members', sa.Column('download_token', sa.String(length=12), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('group_members', 'download_token')
    # ### end Alembic commands ###
