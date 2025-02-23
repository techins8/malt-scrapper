"""Add status field to MaltProfile

Revision ID: efbefffed8d9
Revises: e07842353b59
Create Date: 2025-02-23 16:06:33.186768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum


# revision identifiers, used by Alembic.
revision = 'efbefffed8d9'
down_revision = 'e07842353b59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type first
    status_enum = Enum('TODO', 'IN_PROGRESS', 'ERROR', 'CANCELLED', 'SCRAPPED', 'NOT_FOUND', name='profilestatus')
    status_enum.create(op.get_bind())
    
    # Add column using the enum type
    op.add_column('malt_profiles', sa.Column('status', status_enum, nullable=False, server_default='TODO'))


def downgrade() -> None:
    # Drop the column first
    op.drop_column('malt_profiles', 'status')
    
    # Then drop the enum type
    status_enum = Enum('TODO', 'IN_PROGRESS', 'ERROR', 'CANCELLED', 'SCRAPPED', 'NOT_FOUND', name='profilestatus')
    status_enum.drop(op.get_bind())
