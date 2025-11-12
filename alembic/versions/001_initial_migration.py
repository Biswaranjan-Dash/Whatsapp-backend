"""initial migration

Revision ID: 001
Revises: 
Create Date: 2025-11-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patients_phone'), 'patients', ['phone'], unique=False)

    op.create_table(
        'doctor_masters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('specialty', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    op.create_table(
        'doctor_daily_availabilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('is_present', sa.Boolean(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_masters.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id', 'date', name='uq_doctor_date_availability')
    )
    op.create_index('ix_doctor_availability_date', 'doctor_daily_availabilities', ['doctor_id', 'date'], unique=False)

    op.create_table(
        'doctor_daily_capacities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('remaining', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_masters.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id', 'date', name='uq_doctor_date_capacity')
    )
    op.create_index('ix_doctor_capacity_date', 'doctor_daily_capacities', ['doctor_id', 'date'], unique=False)

    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('slot', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('BOOKED', 'CANCELLED', 'CHECKED_IN', 'COMPLETED', name='appointmentstatus'), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_masters.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('doctor_id', 'date', 'slot', name='uq_doctor_date_slot')
    )
    op.create_index('ix_appointment_date', 'appointments', ['doctor_id', 'date'], unique=False)
    op.create_index('ix_appointment_idempotency', 'appointments', ['idempotency_key'], unique=False)

    op.create_table(
        'queue_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.Enum('WAITING', 'SERVED', 'SKIPPED', name='queuestatus'), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctor_masters.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('appointment_id'),
        sa.UniqueConstraint('doctor_id', 'date', 'position', name='uq_doctor_date_position')
    )
    op.create_index('ix_queue_date', 'queue_entries', ['doctor_id', 'date', 'position'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_queue_date', table_name='queue_entries')
    op.drop_table('queue_entries')
    
    op.drop_index('ix_appointment_idempotency', table_name='appointments')
    op.drop_index('ix_appointment_date', table_name='appointments')
    op.drop_table('appointments')
    
    op.drop_index('ix_doctor_capacity_date', table_name='doctor_daily_capacities')
    op.drop_table('doctor_daily_capacities')
    
    op.drop_index('ix_doctor_availability_date', table_name='doctor_daily_availabilities')
    op.drop_table('doctor_daily_availabilities')
    
    op.drop_table('doctor_masters')
    
    op.drop_index(op.f('ix_patients_phone'), table_name='patients')
    op.drop_table('patients')
    
    sa.Enum(name='appointmentstatus').drop(op.get_bind())
    sa.Enum(name='queuestatus').drop(op.get_bind())
