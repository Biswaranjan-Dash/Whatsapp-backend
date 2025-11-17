from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, text
from sqlalchemy.exc import IntegrityError
from app.models import Appointment, DoctorDailyCapacity, AppointmentStatus


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Appointment]:
        result = await self.db.execute(
            select(Appointment).where(Appointment.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()
    
    async def list_by_doctor_date(self, doctor_id: UUID, appointment_date: date) -> List[Appointment]:
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.date == appointment_date,
                    Appointment.status != AppointmentStatus.CANCELLED
                )
            ).order_by(Appointment.slot)
        )
        return list(result.scalars().all())
    
    async def list_by_date(self, appointment_date: date) -> List[Appointment]:
        """Get all appointments across all doctors for a specific date"""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.date == appointment_date,
                    Appointment.status != AppointmentStatus.CANCELLED
                )
            ).order_by(Appointment.doctor_id, Appointment.slot)
        )
        return list(result.scalars().all())
    
    async def atomic_book_slot(
        self, 
        doctor_id: UUID, 
        appointment_date: date,
        patient_id: UUID,
        idempotency_key: Optional[str] = None
    ) -> Appointment:
        """
        Atomically book a slot using capacity decrement approach.
        Raises IntegrityError if capacity exhausted or slot conflict.
        """
        stmt = (
            update(DoctorDailyCapacity)
            .where(
                and_(
                    DoctorDailyCapacity.doctor_id == doctor_id,
                    DoctorDailyCapacity.date == appointment_date,
                    DoctorDailyCapacity.remaining > 0
                )
            )
            .values(remaining=DoctorDailyCapacity.remaining - 1)
            .returning(DoctorDailyCapacity.capacity, DoctorDailyCapacity.remaining)
        )
        
        result = await self.db.execute(stmt)
        row = result.first()
        
        if not row:
            raise ValueError("No capacity available")
        
        capacity, remaining = row
        slot = capacity - remaining
        
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=appointment_date,
            slot=slot,
            status=AppointmentStatus.BOOKED,
            idempotency_key=idempotency_key
        )
        
        self.db.add(appointment)
        await self.db.commit()
        await self.db.refresh(appointment)
        
        return appointment
    
    async def update_status(self, appointment_id: UUID, status: AppointmentStatus) -> Appointment:
        result = await self.db.execute(
            select(Appointment).where(Appointment.id == appointment_id)
        )
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = status
        await self.db.commit()
        await self.db.refresh(appointment)
        return appointment
