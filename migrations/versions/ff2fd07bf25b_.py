"""empty message

Revision ID: ff2fd07bf25b
Revises: 38ec35f26b2d
Create Date: 2017-11-12 14:09:36.773718

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff2fd07bf25b'
down_revision = '38ec35f26b2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('smstpls', sa.Column('reason', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('smstpls', 'reason')
    # ### end Alembic commands ###
