from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from datetime import date, datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import AppointmentCreate, AppointmentResponse, ErrorResponse
from app.services.appointment_service import AppointmentService
from app.api.v1.deps import get_appointment_service
from app.db.session import get_db
from app.core.logging import get_logger

router = APIRouter(prefix="/appointments", tags=["appointments"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def book_appointment(
    appointment_data: AppointmentCreate,
    service: AppointmentService = Depends(get_appointment_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Book an appointment. 
    Enforces max 10 appointments per doctor per day.
    Supports idempotent booking via idempotency_key.
    """
    try:
        # Generate idempotency key if not provided
        idempotency_key = appointment_data.idempotency_key
        if not idempotency_key:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
            idempotency_key = f"{appointment_data.patient_id}_{appointment_data.doctor_id}_{appointment_data.date}_{timestamp}"
        
        appointment = await service.book_appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_date=appointment_data.date,
            time_slot=appointment_data.time_slot,
            idempotency_key=idempotency_key
        )
        
        # Send real-time notification
        from app.api.v1.routers.websockets import notify_queue_update
        await notify_queue_update(appointment.doctor_id, appointment.date, db)
        
        return appointment
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NotFound", "message": error_msg}
            )
        elif "not available" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={"error": "DoctorUnavailable", "message": error_msg}
            )
        elif "no available slots" in error_msg.lower() or "capacity full" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "CapacityFull", "message": error_msg}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "BookingConflict", "message": error_msg}
            )
    except Exception as e:
        logger.error("Booking failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalError", "message": "Booking failed"}
        )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_appointment(
    appointment_id: UUID,
    service: AppointmentService = Depends(get_appointment_service)
):
    """Get appointment by ID"""
    appointment = await service.get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Appointment {appointment_id} not found"}
        )
    return appointment


@router.get(
    "/doctors/{doctor_id}/appointments",
    response_model=List[AppointmentResponse],
)
async def list_doctor_appointments(
    doctor_id: UUID,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    service: AppointmentService = Depends(get_appointment_service)
):
    """List all appointments for a doctor on a specific date"""
    appointments = await service.list_appointments_by_doctor_date(doctor_id, date)
    return appointments
