"""use id as replacement of uuid

Revision ID: 2cab53e752df
Revises: 49dae90cb44c
Create Date: 2023-11-27 14:04:30.287831

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2cab53e752df"
down_revision = "49dae90cb44c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("invitation_code", schema=None) as batch_op:
        batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
        batch_op.drop_column("uuid")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("invitation_code", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("uuid", sa.UUID(), autoincrement=False, nullable=False)
        )
        batch_op.drop_column("id")

    # ### end Alembic commands ###
