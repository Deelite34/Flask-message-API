"""fix lack of primary key in invitation code

Revision ID: 76762a252eb5
Revises: 97ece227b382
Create Date: 2024-01-23 14:50:21.944152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76762a252eb5'
down_revision = '97ece227b382'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
