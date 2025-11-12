from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import QueueEntry, QueueStatus, Appointment


class QueueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_appointment_id(self, appointment_id: UUID) -> Optional[QueueEntry]:
        result = await self.db.execute(
            select(QueueEntry).where(QueueEntry.appointment_id == appointment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_next_position(self, doctor_id: UUID, queue_date: date) -> int:
        """Get next available position for queue atomically"""
        result = await self.db.execute(
            select(func.coalesce(func.max(QueueEntry.position), 0)).where(
                and_(
                    QueueEntry.doctor_id == doctor_id,
                    QueueEntry.date == queue_date
                )
            )
        )
        max_position = result.scalar_one()
        return max_position + 1
    
    async def create(self, queue_data: dict) -> QueueEntry:
        queue_entry = QueueEntry(**queue_data)
        self.db.add(queue_entry)
        await self.db.commit()
        await self.db.refresh(queue_entry)
        return queue_entry
    
    async def list_by_doctor_date(self, doctor_id: UUID, queue_date: date) -> List[QueueEntry]:
        result = await self.db.execute(
            select(QueueEntry)
            .join(Appointment)
            .where(
                and_(
                    QueueEntry.doctor_id == doctor_id,
                    QueueEntry.date == queue_date
                )
            )
            .order_by(QueueEntry.position)
        )
        return list(result.scalars().all())
