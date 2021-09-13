"""inital migration

Revision ID: b605971f5933
Revises: 
Create Date: 2021-08-27 16:16:25.937557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b605971f5933'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.drop_column('state')
        batch_op.drop_column('f_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.add_column(sa.Column('f_name', sa.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('state', sa.VARCHAR(length=50), nullable=True))

    # ### end Alembic commands ###
