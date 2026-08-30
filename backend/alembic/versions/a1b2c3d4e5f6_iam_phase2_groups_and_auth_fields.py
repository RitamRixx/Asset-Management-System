"""iam phase 2 — groups, password reset tokens, user auth-provider fields

Revision ID: a1b2c3d4e5f6
Revises: 905d66c2055a
Create Date: 2026-08-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '905d66c2055a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Groups (IAM spec section 6): pure AMS org concept, deliberately
    # separate from both Department and any Microsoft Entra group. ---
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name'),
    )
    op.add_column('employees', sa.Column('group_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_employees_group_id', 'employees', 'groups', ['group_id'], ['id'])

    # --- Password reset tokens. Hashed, single-use, short-lived. ---
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash'),
    )

    # --- users: auth provider + external identity + lockout state ---
    authprovider_enum = sa.Enum('LOCAL', 'MICROSOFT', name='authprovider')
    authprovider_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'users',
        sa.Column('auth_provider', authprovider_enum, nullable=False, server_default='LOCAL'),
    )
    op.add_column('users', sa.Column('entra_object_id', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('entra_tenant_id', sa.String(length=100), nullable=True))
    op.add_column(
        'users',
        sa.Column('failed_login_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))

    # Composite unique — Microsoft's oid is unique per-tenant, not globally.
    op.create_unique_constraint(
        'uq_users_entra_identity', 'users', ['entra_object_id', 'entra_tenant_id']
    )

    # Every existing row already has a hash (LOCAL by construction today) —
    # relax NOT NULL so a future MICROSOFT-provider user can omit one.
    # No existing data is touched. authenticate_user() now guards against
    # a NULL hash explicitly, so this is safe ahead of any Entra code path
    # actually creating such a row.
    op.alter_column('users', 'password_hash', existing_type=sa.String(length=255), nullable=True)

    # Postgres requires ALTER TYPE ... ADD VALUE to run outside the
    # migration's normal transactional DDL block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE userstatus ADD VALUE IF NOT EXISTS 'SUSPENDED'")
        op.execute("ALTER TYPE userstatus ADD VALUE IF NOT EXISTS 'PENDING'")


def downgrade() -> None:
    # Note: Postgres can't remove individual enum values via ALTER TYPE.
    # This migration doesn't seed SUSPENDED/PENDING data, so a full
    # downgrade of `userstatus` itself isn't attempted here — if ever
    # needed, rebuild the enum with only ACTIVE/DISABLED and migrate the
    # column across.
    op.alter_column('users', 'password_hash', existing_type=sa.String(length=255), nullable=False)
    op.drop_constraint('uq_users_entra_identity', 'users', type_='unique')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_count')
    op.drop_column('users', 'entra_tenant_id')
    op.drop_column('users', 'entra_object_id')
    op.drop_column('users', 'auth_provider')

    bind = op.get_bind()
    sa.Enum(name='authprovider').drop(bind, checkfirst=True)

    op.drop_table('password_reset_tokens')

    op.drop_constraint('fk_employees_group_id', 'employees', type_='foreignkey')
    op.drop_column('employees', 'group_id')
    op.drop_table('groups')