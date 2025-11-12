from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import DoctorMaster, DoctorDailyAvailability, DoctorDailyCapacity


class DoctorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, doctor_data: dict) -> DoctorMaster:
        doctor = DoctorMaster(**doctor_data)
        self.db.add(doctor)
        await self.db.commit()
        await self.db.refresh(doctor)
        return doctor
    
    async def get_by_id(self, doctor_id: UUID) -> Optional[DoctorMaster]:
        result = await self.db.execute(
            select(DoctorMaster).where(DoctorMaster.id == doctor_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[DoctorMaster]:
        result = await self.db.execute(
            select(DoctorMaster).where(DoctorMaster.code == code)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self) -> List[DoctorMaster]:
        result = await self.db.execute(select(DoctorMaster))
        return list(result.scalars().all())
    
    async def upsert_availability(
        self, doctor_id: UUID, availability_date: date, is_present: bool, notes: Optional[str] = None
    ) -> DoctorDailyAvailability:
        result = await self.db.execute(
            select(DoctorDailyAvailability).where(
                and_(
                    DoctorDailyAvailability.doctor_id == doctor_id,
                    DoctorDailyAvailability.date == availability_date
                )
            )
        )
        availability = result.scalar_one_or_none()
        
        if availability:
            availability.is_present = is_present
            availability.notes = notes
        else:
            availability = DoctorDailyAvailability(
                doctor_id=doctor_id,
                date=availability_date,
                is_present=is_present,
                notes=notes
            )
            self.db.add(availability)
        
        await self.db.commit()
        await self.db.refresh(availability)
        return availability
    
    async def get_availability(self, doctor_id: UUID, availability_date: date) -> Optional[DoctorDailyAvailability]:
        result = await self.db.execute(
            select(DoctorDailyAvailability).where(
                and_(
                    DoctorDailyAvailability.doctor_id == doctor_id,
                    DoctorDailyAvailability.date == availability_date
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_capacity(
        self, doctor_id: UUID, capacity_date: date, default_capacity: int = 10
    ) -> DoctorDailyCapacity:
        result = await self.db.execute(
            select(DoctorDailyCapacity).where(
                and_(
                    DoctorDailyCapacity.doctor_id == doctor_id,
                    DoctorDailyCapacity.date == capacity_date
                )
            )
        )
        capacity = result.scalar_one_or_none()
        
        if not capacity:
            capacity = DoctorDailyCapacity(
                doctor_id=doctor_id,
                date=capacity_date,
                capacity=default_capacity,
                remaining=default_capacity
            )
            self.db.add(capacity)
            await self.db.commit()
            await self.db.refresh(capacity)
        
        return capacity
    
    async def get_capacity(self, doctor_id: UUID, capacity_date: date) -> Optional[DoctorDailyCapacity]:
        result = await self.db.execute(
            select(DoctorDailyCapacity).where(
                and_(
                    DoctorDailyCapacity.doctor_id == doctor_id,
                    DoctorDailyCapacity.date == capacity_date
                )
            )
        )
        return result.scalar_one_or_none()
