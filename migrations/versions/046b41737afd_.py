"""empty message

Revision ID: 046b41737afd
Revises: 
Create Date: 2017-06-13 21:55:50.576084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '046b41737afd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('uid', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('password_change_time', sa.Integer(), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('telephone', sa.String(length=11), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('log_level', sa.Integer(), nullable=True),
    sa.Column('email_confirmed', sa.Boolean(), nullable=True),
    sa.Column('telephone_confirmed', sa.Boolean(), nullable=True),
    sa.Column('telephone_confirmed_code', sa.String(length=6), nullable=True),
    sa.Column('telephone_confirmed_code_time', sa.Integer(), nullable=True),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('last_login_time', sa.Integer(), nullable=True),
    sa.Column('this_login_time', sa.Integer(), nullable=True),
    sa.Column('useful_token', sa.String(length=256), nullable=True),
    sa.Column('student_card', sa.String(length=128), nullable=True),
    sa.Column('student_auth', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('image', sa.LargeBinary(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('role_json', sa.Text(), nullable=True),
    sa.Column('tel', sa.String(length=11), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('money_billings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('create_time', sa.Integer(), nullable=True),
    sa.Column('finish_time', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('token', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('rec_id', sa.Integer(), nullable=True),
    sa.Column('from_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['from_id'], ['users.uid'], ),
    sa.ForeignKeyConstraint(['rec_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('last_seen', sa.Integer(), nullable=True),
    sa.Column('this_seen', sa.Integer(), nullable=True),
    sa.Column('permission_level', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('billings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('out_account_id', sa.Integer(), nullable=True),
    sa.Column('in_group_id', sa.Integer(), nullable=True),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('deal_state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['in_group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['out_account_id'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('forms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('form_data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('tel', sa.String(length=11), nullable=True),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('address', sa.String(length=128), nullable=True),
    sa.Column('gender', sa.Boolean(), nullable=True),
    sa.Column('role_alias', sa.Integer(), nullable=True),
    sa.Column('other', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('formdatas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('form_id', sa.Integer(), nullable=True),
    sa.Column('image', sa.LargeBinary(), nullable=True),
    sa.Column('data', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('msmrecords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Integer(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('msmrecords')
    op.drop_table('formdatas')
    op.drop_table('members')
    op.drop_table('forms')
    op.drop_table('billings')
    op.drop_table('admins')
    op.drop_table('pms')
    op.drop_table('money_billings')
    op.drop_table('groups')
    op.drop_table('users')
    # ### end Alembic commands ###
