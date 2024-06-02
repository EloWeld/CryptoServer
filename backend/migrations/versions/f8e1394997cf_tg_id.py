"""Tg id

Revision ID: f8e1394997cf
Revises: f730ab622d66
Create Date: 2024-06-02 01:44:12.714868

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8e1394997cf'
down_revision = 'f730ab622d66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('tg_id', sa.BigInteger(), nullable=True))
    op.drop_column('settings', 'tg_users_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('tg_users_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_column('settings', 'tg_id')
    # ### end Alembic commands ###
