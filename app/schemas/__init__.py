from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date
from uuid import UUID
import re


class PatientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    
    @field_validator('phone')
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        cleaned = re.sub(r'[^\d+]', '', v)
        if not cleaned:
            raise ValueError('Phone must contain digits')
        return cleaned


class PatientResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: Optional[str]
    age: Optional[int]
    phone: str
    email: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    specialty: Optional[str] = Field(None, max_length=100)


class DoctorResponse(BaseModel):
    id: UUID
    name: str
    code: str
    specialty: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilityUpsert(BaseModel):
    date: date
    is_present: bool
    notes: Optional[str] = None


class AvailabilityResponse(BaseModel):
    id: Optional[UUID] = None
    doctor_id: UUID
    date: date
    is_present: bool
    notes: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    date: date
    idempotency_key: Optional[str] = Field(None, max_length=255)


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    date: date
    slot: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    appointment_id: UUID
    patient_id: UUID


class CheckInResponse(BaseModel):
    queue_position: int
    checked_in_at: datetime
    appointment_id: UUID
    
    class Config:
        from_attributes = True


class QueueEntryResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    doctor_id: UUID
    date: date
    position: int
    checked_in_at: datetime
    status: str
    patient_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
