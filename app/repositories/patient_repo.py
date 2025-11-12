from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Patient


class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, patient_data: dict) -> Patient:
        patient = Patient(**patient_data)
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient
    
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[Patient]:
        result = await self.db.execute(
            select(Patient).where(Patient.phone == phone)
        )
        return result.scalar_one_or_none()
