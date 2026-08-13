"""Create planning_version, schedule_item, schedule_gantt, execution_log tables

Revision ID: 002_add_planning_tables
Revises: 001_initial_schema
Create Date: 2026-05-08

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_planning_tables'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── planning_version ──────────────────────────────────────────────────────
    op.create_table(
        'planning_version',
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['technician_id'], ['technician.technician_id'], ),
        sa.PrimaryKeyConstraint('version_id')
    )
    op.create_index(
        op.f('ix_planning_version_technician_id'),
        'planning_version',
        ['technician_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_planning_version_is_active'),
        'planning_version',
        ['is_active'],
        unique=False
    )

    # ── schedule_item ─────────────────────────────────────────────────────────
    op.create_table(
        'schedule_item',
        sa.Column('schedule_item_id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('demand_manager_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('worked_hours', sa.Float(), nullable=False),
        sa.Column('distance', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['demand_manager_id'], ['demand_manager.demand_manager_id'], ),
        sa.ForeignKeyConstraint(['technician_id'], ['technician.technician_id'], ),
        sa.ForeignKeyConstraint(['version_id'], ['planning_version.version_id'], ),
        sa.PrimaryKeyConstraint('schedule_item_id')
    )
    op.create_index(
        op.f('ix_schedule_item_version_id'),
        'schedule_item',
        ['version_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_schedule_item_demand_manager_id'),
        'schedule_item',
        ['demand_manager_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_schedule_item_technician_id'),
        'schedule_item',
        ['technician_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_schedule_item_scheduled_date'),
        'schedule_item',
        ['scheduled_date'],
        unique=False
    )

    # ── schedule_gantt ────────────────────────────────────────────────────────
    op.create_table(
        'schedule_gantt',
        sa.Column('schedule_gantt_id', sa.Integer(), nullable=False),
        sa.Column('version_id', sa.Integer(), nullable=False),
        sa.Column('demand_manager_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('finish_date', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['demand_manager_id'], ['demand_manager.demand_manager_id'], ),
        sa.ForeignKeyConstraint(['technician_id'], ['technician.technician_id'], ),
        sa.ForeignKeyConstraint(['version_id'], ['planning_version.version_id'], ),
        sa.PrimaryKeyConstraint('schedule_gantt_id')
    )
    op.create_index(
        op.f('ix_schedule_gantt_version_id'),
        'schedule_gantt',
        ['version_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_schedule_gantt_demand_manager_id'),
        'schedule_gantt',
        ['demand_manager_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_schedule_gantt_technician_id'),
        'schedule_gantt',
        ['technician_id'],
        unique=False
    )

    # ── execution_log ─────────────────────────────────────────────────────────
    op.create_table(
        'execution_log',
        sa.Column('execution_log_id', sa.Integer(), nullable=False),
        sa.Column('demand_manager_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=False),
        sa.Column('execution_date', sa.Date(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('distance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('worked_hours', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['demand_manager_id'], ['demand_manager.demand_manager_id'], ),
        sa.ForeignKeyConstraint(['technician_id'], ['technician.technician_id'], ),
        sa.PrimaryKeyConstraint('execution_log_id')
    )
    op.create_index(
        op.f('ix_execution_log_demand_manager_id'),
        'execution_log',
        ['demand_manager_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_execution_log_technician_id'),
        'execution_log',
        ['technician_id'],
        unique=False
    )
    op.create_index(
        op.f('ix_execution_log_execution_date'),
        'execution_log',
        ['execution_date'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_execution_log_execution_date'), table_name='execution_log')
    op.drop_index(op.f('ix_execution_log_technician_id'), table_name='execution_log')
    op.drop_index(op.f('ix_execution_log_demand_manager_id'), table_name='execution_log')
    op.drop_table('execution_log')

    op.drop_index(op.f('ix_schedule_gantt_technician_id'), table_name='schedule_gantt')
    op.drop_index(op.f('ix_schedule_gantt_demand_manager_id'), table_name='schedule_gantt')
    op.drop_index(op.f('ix_schedule_gantt_version_id'), table_name='schedule_gantt')
    op.drop_table('schedule_gantt')

    op.drop_index(op.f('ix_schedule_item_scheduled_date'), table_name='schedule_item')
    op.drop_index(op.f('ix_schedule_item_technician_id'), table_name='schedule_item')
    op.drop_index(op.f('ix_schedule_item_demand_manager_id'), table_name='schedule_item')
    op.drop_index(op.f('ix_schedule_item_version_id'), table_name='schedule_item')
    op.drop_table('schedule_item')

    op.drop_index(op.f('ix_planning_version_is_active'), table_name='planning_version')
    op.drop_index(op.f('ix_planning_version_technician_id'), table_name='planning_version')
    op.drop_table('planning_version')