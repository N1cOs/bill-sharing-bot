"""change debt model

Revision ID: 879f7d889421
Revises: 9ee5e7751caa
Create Date: 2019-07-12 23:53:43.749900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '879f7d889421'
down_revision = '9ee5e7751caa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('debt', sa.Column('is_monthly', sa.Boolean(), nullable=True))
    op.drop_column('debt', 'period')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('debt', sa.Column('period', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('debt', 'is_monthly')
    # ### end Alembic commands ###