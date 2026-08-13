"""create_base_tables

Revision ID: 001_initial_schema
Revises: --
Create Date: 2026-08-13 20:17:07.880330

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('city',
        sa.Column('city_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('city_name', sa.String(), nullable=False),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('country', sa.String(), nullable=False),
        sa.Column('geolocation_lat', sa.Float(), nullable=False),
        sa.Column('geolocation_lon', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('city_id')
    )
    op.create_table('analyst',
        sa.Column('analyst_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('analyst_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('contact', sa.String(), nullable=False),
        sa.Column('creation_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('valid_to_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('analyst_id'),
        sa.UniqueConstraint('email')
    )
    op.create_table('customer',
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('short_name', sa.String(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('segment', sa.String(), nullable=False),
        sa.Column('sub_segment', sa.String(), nullable=False),
        sa.Column('region', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['city_id'], ['city.city_id']),
        sa.PrimaryKeyConstraint('customer_id')
    )
    op.create_table('project',
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('project_name', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.customer_id']),
        sa.PrimaryKeyConstraint('project_id')
    )
    op.create_table('technician',
        sa.Column('technician_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('technician_name', sa.String(), nullable=False),
        sa.Column('creation_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('dismiss_date', sa.Date(), nullable=True),
        sa.Column('position', sa.String(), nullable=False),
        sa.Column('base_location_city_id', sa.Integer(), nullable=False),
        sa.Column('current_location_city_id', sa.Integer(), nullable=False),
        sa.Column('daily_capacity', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['base_location_city_id'], ['city.city_id']),
        sa.ForeignKeyConstraint(['current_location_city_id'], ['city.city_id']),
        sa.PrimaryKeyConstraint('technician_id')
    )
    op.create_table('demand',
        sa.Column('demand_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('demand_title', sa.String(), nullable=False),
        sa.Column('problem_description', sa.String(), nullable=False),
        sa.Column('request_date', sa.Date(), nullable=False),
        sa.Column('responsible_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('estimated_time', sa.Float(), nullable=False),
        sa.Column('actual_time', sa.Float(), nullable=True),
        sa.Column('technical_visit_reason', sa.String(), nullable=False),
        sa.Column('causal_sector', sa.String(), nullable=False),
        sa.Column('causal_area', sa.String(), nullable=False),
        sa.Column('root_cause', sa.String(), nullable=False),
        sa.Column('equipment', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['project.project_id']),
        sa.ForeignKeyConstraint(['responsible_id'], ['analyst.analyst_id']),
        sa.PrimaryKeyConstraint('demand_id')
    )
    op.create_table('demand_manager',
        sa.Column('demand_manager_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('demand_id', sa.Integer(), nullable=False),
        sa.Column('technician_id', sa.Integer(), nullable=False),
        sa.Column('next_demand_manager_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('finish_date', sa.Date(), nullable=True),
        sa.Column('travel_time', sa.Float(), nullable=True),
        sa.Column('travel_distance', sa.Float(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['demand_id'], ['demand.demand_id']),
        sa.ForeignKeyConstraint(['technician_id'], ['technician.technician_id']),
        sa.ForeignKeyConstraint(['next_demand_manager_id'], ['demand_manager.demand_manager_id']),
        sa.PrimaryKeyConstraint('demand_manager_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('demand_manager')
    op.drop_table('demand')
    op.drop_table('technician')
    op.drop_table('project')
    op.drop_table('customer')
    op.drop_table('analyst')
    op.drop_table('city')
