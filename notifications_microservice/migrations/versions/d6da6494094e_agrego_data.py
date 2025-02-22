"""agrego data

Revision ID: d6da6494094e
Revises: 8af117fb5f5f
Create Date: 2021-02-21 20:48:58.080951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6da6494094e'
down_revision = '8af117fb5f5f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'scheduled_notification', sa.Column('_data', sa.JSON(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scheduled_notification', '_data')
    # ### end Alembic commands ###
