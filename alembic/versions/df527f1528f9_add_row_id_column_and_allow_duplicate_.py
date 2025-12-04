"""Add row_id column and allow duplicate doc_no

Revision ID: df527f1528f9
Revises: 45f09f84b4e3
Create Date: 2025-12-04 15:08:17.429089

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df527f1528f9'
down_revision: Union[str, Sequence[str], None] = '45f09f84b4e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add row_id to expenses and remove unique constraint from doc_no
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.add_column(sa.Column('row_id', sa.String(), nullable=True))
        batch_op.drop_index('ix_expenses_doc_no')
        batch_op.create_index('ix_expenses_doc_no', ['doc_no'], unique=False)
        batch_op.create_index('ix_expenses_row_id', ['row_id'], unique=True)

    # Add row_id to income and remove unique constraint from doc_no
    with op.batch_alter_table('income') as batch_op:
        batch_op.add_column(sa.Column('row_id', sa.String(), nullable=True))
        batch_op.drop_index('ix_income_doc_no')
        batch_op.create_index('ix_income_doc_no', ['doc_no'], unique=False)
        batch_op.create_index('ix_income_row_id', ['row_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.drop_index('ix_expenses_row_id')
        batch_op.drop_column('row_id')
        batch_op.drop_index('ix_expenses_doc_no')
        batch_op.create_index('ix_expenses_doc_no', ['doc_no'], unique=True)

    with op.batch_alter_table('income') as batch_op:
        batch_op.drop_index('ix_income_row_id')
        batch_op.drop_column('row_id')
        batch_op.drop_index('ix_income_doc_no')
        batch_op.create_index('ix_income_doc_no', ['doc_no'], unique=True)
