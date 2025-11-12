from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.patient_repo import PatientRepository
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.queue_repo import QueueRepository
from app.services.patient_service import PatientService
from app.services.doctor_service import DoctorService
from app.services.appointment_service import AppointmentService
from app.services.queue_service import QueueService


def get_patient_repo(db: AsyncSession = Depends(get_db)) -> PatientRepository:
    return PatientRepository(db)


def get_doctor_repo(db: AsyncSession = Depends(get_db)) -> DoctorRepository:
    return DoctorRepository(db)


def get_appointment_repo(db: AsyncSession = Depends(get_db)) -> AppointmentRepository:
    return AppointmentRepository(db)


def get_queue_repo(db: AsyncSession = Depends(get_db)) -> QueueRepository:
    return QueueRepository(db)


def get_patient_service(
    repo: PatientRepository = Depends(get_patient_repo)
) -> PatientService:
    return PatientService(repo)


def get_doctor_service(
    repo: DoctorRepository = Depends(get_doctor_repo)
) -> DoctorService:
    return DoctorService(repo)


def get_appointment_service(
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
    doctor_repo: DoctorRepository = Depends(get_doctor_repo),
) -> AppointmentService:
    return AppointmentService(appointment_repo, doctor_repo)


def get_queue_service(
    queue_repo: QueueRepository = Depends(get_queue_repo),
    appointment_repo: AppointmentRepository = Depends(get_appointment_repo),
) -> QueueService:
    return QueueService(queue_repo, appointment_repo)
