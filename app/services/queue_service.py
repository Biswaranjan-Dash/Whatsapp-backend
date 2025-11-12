from typing import List
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from app.repositories.queue_repo import QueueRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.models import QueueEntry, AppointmentStatus, QueueStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class QueueService:
    def __init__(self, queue_repo: QueueRepository, appointment_repo: AppointmentRepository):
        self.queue_repo = queue_repo
        self.appointment_repo = appointment_repo
    
    async def check_in(self, appointment_id: UUID, patient_id: UUID) -> QueueEntry:
        """
        Check in a patient for their appointment.
        Only allowed on appointment date. Atomically assigns queue position.
        """
        appointment = await self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.patient_id != patient_id:
            raise ValueError("Appointment does not belong to this patient")
        
        if appointment.status != AppointmentStatus.BOOKED:
            raise ValueError(f"Appointment is already {appointment.status.value}")
        
        today = date.today()
        if appointment.date != today:
            raise ValueError(f"Check-in only allowed on appointment date. Appointment is for {appointment.date}")
        
        existing_queue = await self.queue_repo.get_by_appointment_id(appointment_id)
        if existing_queue:
            logger.warning("Duplicate check-in attempt", appointment_id=str(appointment_id))
            raise ValueError("Already checked in")
        
        next_position = await self.queue_repo.get_next_position(appointment.doctor_id, appointment.date)
        
        try:
            queue_entry = await self.queue_repo.create({
                "appointment_id": appointment_id,
                "doctor_id": appointment.doctor_id,
                "date": appointment.date,
                "position": next_position,
                "status": QueueStatus.WAITING
            })
            
            await self.appointment_repo.update_status(appointment_id, AppointmentStatus.CHECKED_IN)
            
            logger.info(
                "Patient checked in",
                appointment_id=str(appointment_id),
                queue_position=next_position,
                doctor_id=str(appointment.doctor_id)
            )
            
            return queue_entry
            
        except IntegrityError:
            logger.error("Check-in failed - constraint violation", appointment_id=str(appointment_id))
            raise ValueError("Check-in conflict - please retry")
    
    async def get_queue_for_doctor(self, doctor_id: UUID, queue_date: date) -> List[QueueEntry]:
        """Get ordered queue for a doctor on a specific date"""
        return await self.queue_repo.list_by_doctor_date(doctor_id, queue_date)
