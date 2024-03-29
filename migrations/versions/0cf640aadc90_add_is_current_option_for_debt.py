"""add is_current option for debt

Revision ID: 0cf640aadc90
Revises: 91a06429ceb8
Create Date: 2019-08-14 21:17:55.710782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cf640aadc90'
down_revision = '91a06429ceb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('debt', sa.Column('is_current', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('debt', 'is_current')
    # ### end Alembic commands ###
