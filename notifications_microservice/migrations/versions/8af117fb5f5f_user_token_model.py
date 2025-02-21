"""user token model

Revision ID: 8af117fb5f5f
Revises: d0c05d22ecb6
Create Date: 2020-12-27 22:43:16.538952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8af117fb5f5f'
down_revision = 'd0c05d22ecb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_token',
    sa.Column('user_id', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('push_token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_token')
    # ### end Alembic commands ###
