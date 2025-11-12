from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.doctor_repo import DoctorRepository
from app.models import Appointment, AppointmentStatus
from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class AppointmentService:
    def __init__(self, appointment_repo: AppointmentRepository, doctor_repo: DoctorRepository):
        self.appointment_repo = appointment_repo
        self.doctor_repo = doctor_repo
    
    async def book_appointment(
        self,
        patient_id: UUID,
        doctor_id: UUID,
        appointment_date: date,
        idempotency_key: Optional[str] = None
    ) -> Appointment:
        """
        Book an appointment with concurrency-safe slot allocation.
        Enforces max appointments per doctor per day and doctor availability.
        Supports idempotent booking via idempotency_key.
        """
        if idempotency_key:
            existing = await self.appointment_repo.get_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(
                    "Idempotent booking - returning existing appointment",
                    appointment_id=str(existing.id),
                    idempotency_key=idempotency_key
                )
                return existing
        
        doctor = await self.doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise ValueError(f"Doctor {doctor_id} not found")
        
        availability = await self.doctor_repo.get_availability(doctor_id, appointment_date)
        if availability and not availability.is_present:
            raise ValueError(f"Doctor is not available on {appointment_date}")
        
        await self.doctor_repo.get_or_create_capacity(
            doctor_id, 
            appointment_date, 
            settings.MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY
        )
        
        try:
            appointment = await self.appointment_repo.atomic_book_slot(
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                patient_id=patient_id,
                idempotency_key=idempotency_key
            )
            
            logger.info(
                "Appointment booked",
                appointment_id=str(appointment.id),
                doctor_id=str(doctor_id),
                patient_id=str(patient_id),
                date=str(appointment_date),
                slot=appointment.slot
            )
            
            return appointment
            
        except ValueError as e:
            logger.warning(
                "Booking failed - capacity full",
                doctor_id=str(doctor_id),
                date=str(appointment_date)
            )
            raise ValueError("No available slots for this doctor on this date")
        except IntegrityError as e:
            logger.error("Booking failed - integrity error", error=str(e))
            raise ValueError("Slot conflict - please retry")
    
    async def get_appointment(self, appointment_id: UUID) -> Optional[Appointment]:
        """Get appointment by ID"""
        return await self.appointment_repo.get_by_id(appointment_id)
    
    async def list_appointments_by_doctor_date(
        self, doctor_id: UUID, appointment_date: date
    ) -> List[Appointment]:
        """List all appointments for a doctor on a specific date"""
        return await self.appointment_repo.list_by_doctor_date(doctor_id, appointment_date)
