import uuid
from datetime import datetime, date as dt
from typing import Optional
from sqlalchemy import String, Integer, Boolean, Text, Date, DateTime, ForeignKey, UniqueConstraint, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import enum


class Base(DeclarativeBase):
    pass


class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"


class QueueStatus(str, enum.Enum):
    WAITING = "waiting"
    SERVED = "served"
    SKIPPED = "skipped"


class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="patient")


class DoctorMaster(Base):
    __tablename__ = "doctor_masters"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    availabilities: Mapped[list["DoctorDailyAvailability"]] = relationship("DoctorDailyAvailability", back_populates="doctor")
    capacities: Mapped[list["DoctorDailyCapacity"]] = relationship("DoctorDailyCapacity", back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship("Appointment", back_populates="doctor")
    queue_entries: Mapped[list["QueueEntry"]] = relationship("QueueEntry", back_populates="doctor")


class DoctorDailyAvailability(Base):
    __tablename__ = "doctor_daily_availabilities"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctor_masters.id"), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False)
    is_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    doctor: Mapped["DoctorMaster"] = relationship("DoctorMaster", back_populates="availabilities")
    
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", name="uq_doctor_date_availability"),
        Index("ix_doctor_availability_date", "doctor_id", "date"),
    )


class DoctorDailyCapacity(Base):
    __tablename__ = "doctor_daily_capacities"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctor_masters.id"), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    remaining: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    
    doctor: Mapped["DoctorMaster"] = relationship("DoctorMaster", back_populates="capacities")
    
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", name="uq_doctor_date_capacity"),
        Index("ix_doctor_capacity_date", "doctor_id", "date"),
    )


class Appointment(Base):
    __tablename__ = "appointments"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctor_masters.id"), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False)
    slot: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.BOOKED)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["DoctorMaster"] = relationship("DoctorMaster", back_populates="appointments")
    queue_entry: Mapped[Optional["QueueEntry"]] = relationship("QueueEntry", back_populates="appointment", uselist=False)
    
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", "slot", name="uq_doctor_date_slot"),
        Index("ix_appointment_date", "doctor_id", "date"),
        Index("ix_appointment_idempotency", "idempotency_key"),
    )


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("appointments.id"), nullable=False, unique=True)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("doctor_masters.id"), nullable=False)
    date: Mapped[dt] = mapped_column(Date, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    status: Mapped[QueueStatus] = mapped_column(SQLEnum(QueueStatus), nullable=False, default=QueueStatus.WAITING)
    
    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="queue_entry")
    doctor: Mapped["DoctorMaster"] = relationship("DoctorMaster", back_populates="queue_entries")
    
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", "position", name="uq_doctor_date_position"),
        Index("ix_queue_date", "doctor_id", "date", "position"),
    )
