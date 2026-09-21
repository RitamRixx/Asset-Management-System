"""phase a org hierarchy

Revision ID: f1g2h3i4j5k6
Revises: 1022437f20e7
Create Date: 2026-09-20 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1g2h3i4j5k6'
down_revision: Union[str, None] = '1022437f20e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Tables
    op.create_table('org_unit_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('typical_rank', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )

    op.create_table('org_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('unit_type_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['org_units.id'], ),
        sa.ForeignKeyConstraint(['unit_type_id'], ['org_unit_types.id'], ),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], name='fk_org_units_manager_id', use_alter=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_org_units_parent_id'), 'org_units', ['parent_id'], unique=False)
    op.create_index(op.f('ix_org_units_unit_type_id'), 'org_units', ['unit_type_id'], unique=False)

    # 2. Add columns to employees and assets
    op.add_column('employees', sa.Column('org_unit_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_employees_org_unit_id'), 'employees', ['org_unit_id'], unique=False)
    op.create_foreign_key('fk_employees_org_unit_id', 'employees', 'org_units', ['org_unit_id'], ['id'])

    op.add_column('assets', sa.Column('org_unit_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_assets_org_unit_id'), 'assets', ['org_unit_id'], unique=False)
    op.create_foreign_key('fk_assets_org_unit_id', 'assets', 'org_units', ['org_unit_id'], ['id'])

    # 3. Data Backfill
    conn = op.get_bind()

    # Insert org unit types
    types = ["Corporate Office", "Regional Office", "Project", "Project Site", "Site Office", "Department"]
    for i, t_name in enumerate(types):
        conn.execute(sa.text("INSERT INTO org_unit_types (name, typical_rank) VALUES (:name, :rank)"), {"name": t_name, "rank": i+1})
    
    # Get type IDs
    corp_type_id = conn.execute(sa.text("SELECT id FROM org_unit_types WHERE name='Corporate Office'")).scalar()
    dept_type_id = conn.execute(sa.text("SELECT id FROM org_unit_types WHERE name='Department'")).scalar()

    # Migrate Location -> Corporate Office Root Node
    locations = conn.execute(sa.text("SELECT id, name, address, city, state, country, status FROM locations")).fetchall()
    
    root_org_unit_id = None
    if locations:
        loc = locations[0]
        res = conn.execute(
            sa.text("""
                INSERT INTO org_units (name, unit_type_id, address, city, state, country, status)
                VALUES (:name, :type_id, :addr, :city, :state, :country, :status)
                RETURNING id
            """),
            {"name": loc.name, "type_id": corp_type_id, "addr": loc.address, "city": loc.city, "state": loc.state, "country": loc.country, "status": loc.status}
        )
        root_org_unit_id = res.scalar()
    else:
        res = conn.execute(
            sa.text("""
                INSERT INTO org_units (name, unit_type_id)
                VALUES ('Corporate HQ', :type_id)
                RETURNING id
            """),
            {"type_id": corp_type_id}
        )
        root_org_unit_id = res.scalar()

    # Migrate Departments -> OrgUnits (children of root)
    dept_mapping = {} # department_id -> org_unit_id
    departments = conn.execute(sa.text("SELECT id, name, code, manager_id, status FROM departments")).fetchall()
    for dept in departments:
        res = conn.execute(
            sa.text("""
                INSERT INTO org_units (name, code, unit_type_id, parent_id, manager_id, status)
                VALUES (:name, :code, :type_id, :parent_id, :manager_id, :status)
                RETURNING id
            """),
            {
                "name": dept.name, 
                "code": dept.code, 
                "type_id": dept_type_id, 
                "parent_id": root_org_unit_id,
                "manager_id": dept.manager_id,
                "status": dept.status
            }
        )
        dept_mapping[dept.id] = res.scalar()

    # Update Employees
    employees = conn.execute(sa.text("SELECT id, department_id, location_id FROM employees")).fetchall()
    for emp in employees:
        new_org_unit_id = dept_mapping.get(emp.department_id) if emp.department_id else root_org_unit_id
        if new_org_unit_id:
            conn.execute(
                sa.text("UPDATE employees SET org_unit_id = :org_unit_id WHERE id = :id"),
                {"org_unit_id": new_org_unit_id, "id": emp.id}
            )

    # Update Assets
    if root_org_unit_id:
        conn.execute(
            sa.text("UPDATE assets SET org_unit_id = :org_unit_id WHERE location_id IS NOT NULL"),
            {"org_unit_id": root_org_unit_id}
        )


def downgrade() -> None:
    op.drop_constraint('fk_assets_org_unit_id', 'assets', type_='foreignkey')
    op.drop_index(op.f('ix_assets_org_unit_id'), table_name='assets')
    op.drop_column('assets', 'org_unit_id')

    op.drop_constraint('fk_employees_org_unit_id', 'employees', type_='foreignkey')
    op.drop_index(op.f('ix_employees_org_unit_id'), table_name='employees')
    op.drop_column('employees', 'org_unit_id')

    op.drop_table('org_units')
    op.drop_table('org_unit_types')
