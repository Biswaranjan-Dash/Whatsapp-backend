from typing import Optional, List
from uuid import UUID
from datetime import date
from app.repositories.doctor_repo import DoctorRepository
from app.models import DoctorMaster, DoctorDailyAvailability
from app.core.logging import get_logger

logger = get_logger(__name__)


class DoctorService:
    def __init__(self, repo: DoctorRepository):
        self.repo = repo
    
    async def create_doctor(self, doctor_data: dict) -> DoctorMaster:
        """Create a new doctor"""
        existing = await self.repo.get_by_code(doctor_data["code"])
        if existing:
            raise ValueError(f"Doctor with code {doctor_data['code']} already exists")
        
        doctor = await self.repo.create(doctor_data)
        logger.info("Doctor created", doctor_id=str(doctor.id), code=doctor.code)
        return doctor
    
    async def get_doctor(self, doctor_id: UUID) -> Optional[DoctorMaster]:
        """Get doctor by ID"""
        return await self.repo.get_by_id(doctor_id)
    
    async def list_doctors(self) -> List[DoctorMaster]:
        """List all doctors"""
        return await self.repo.list_all()
    
    async def upsert_availability(
        self, doctor_id: UUID, availability_date: date, is_present: bool, notes: Optional[str] = None
    ) -> DoctorDailyAvailability:
        """Set or update doctor availability for a date"""
        doctor = await self.repo.get_by_id(doctor_id)
        if not doctor:
            raise ValueError(f"Doctor {doctor_id} not found")
        
        availability = await self.repo.upsert_availability(
            doctor_id, availability_date, is_present, notes
        )
        logger.info(
            "Doctor availability updated",
            doctor_id=str(doctor_id),
            date=str(availability_date),
            is_present=is_present
        )
        return availability
    
    async def get_availability(
        self, doctor_id: UUID, availability_date: date
    ) -> Optional[DoctorDailyAvailability]:
        """Get doctor availability for a specific date"""
        return await self.repo.get_availability(doctor_id, availability_date)
