"""add all model

Revision ID: 9ee5e7751caa
Revises: 
Create Date: 2019-07-02 01:06:00.865426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ee5e7751caa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('city',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('app_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('second_name', sa.String(length=60), nullable=False),
    sa.Column('gender', sa.String(length=1), nullable=False),
    sa.Column('id_city', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_city'], ['city.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('debt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('amount', sa.Float(precision=24), nullable=True),
    sa.Column('id_lender', sa.Integer(), nullable=True),
    sa.Column('id_conversation', sa.Integer(), nullable=True),
    sa.Column('is_current', sa.Boolean(), nullable=True),
    sa.Column('period', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_lender'], ['app_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_debt', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_debt'], ['debt.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['app_user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_debt',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('debt_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['debt_id'], ['debt.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_debt')
    op.drop_table('payment')
    op.drop_table('debt')
    op.drop_table('app_user')
    op.drop_table('city')
    # ### end Alembic commands ###
