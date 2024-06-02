"""Added timezone_offset

Revision ID: bdd9af1edb88
Revises: 1ee16b020db1
Create Date: 2024-06-01 13:55:03.253933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdd9af1edb88'
down_revision = '1ee16b020db1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('timezone_offset', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'timezone_offset')
    # ### end Alembic commands ###
