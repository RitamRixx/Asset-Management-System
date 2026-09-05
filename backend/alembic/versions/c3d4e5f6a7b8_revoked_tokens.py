"""revoked tokens denylist (IAM Phase 9)

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-09-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        # Mirrors the token's own exp — lets a cleanup job purge rows for
        # tokens that would have expired naturally anyway, instead of the
        # table growing forever.
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti'),
    )
    op.create_index('ix_revoked_tokens_jti', 'revoked_tokens', ['jti'])


def downgrade() -> None:
    op.drop_index('ix_revoked_tokens_jti', table_name='revoked_tokens')
    op.drop_table('revoked_tokens')