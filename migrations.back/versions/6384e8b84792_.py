"""empty message

Revision ID: 6384e8b84792
Revises: ff2fd07bf25b
Create Date: 2018-01-07 17:22:29.775261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6384e8b84792'
down_revision = 'ff2fd07bf25b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data', sa.String(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('group_members')
    # ### end Alembic commands ###
