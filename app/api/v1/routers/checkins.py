from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from datetime import date
from typing import List
from app.schemas import CheckInRequest, CheckInResponse, QueueEntryResponse, ErrorResponse
from app.services.queue_service import QueueService
from app.api.v1.deps import get_queue_service
from app.core.logging import get_logger

router = APIRouter(prefix="/checkins", tags=["checkins"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def check_in(
    checkin_data: CheckInRequest,
    service: QueueService = Depends(get_queue_service)
):
    """
    Check in a patient for their appointment.
    Only allowed on the appointment date.
    Atomically assigns queue position.
    """
    try:
        queue_entry = await service.check_in(
            appointment_id=checkin_data.appointment_id,
            patient_id=checkin_data.patient_id
        )
        return CheckInResponse(
            queue_position=queue_entry.position,
            checked_in_at=queue_entry.checked_in_at,
            appointment_id=queue_entry.appointment_id
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "NotFound", "message": error_msg}
            )
        elif "already checked in" in error_msg.lower() or "is already checked_in" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "AlreadyCheckedIn", "message": error_msg}
            )
        elif "only allowed on appointment date" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"error": "InvalidDate", "message": error_msg}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "ValidationError", "message": error_msg}
            )
    except Exception as e:
        logger.error("Check-in failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalError", "message": "Check-in failed"}
        )


@router.get(
    "/doctors/{doctor_id}/queue",
    response_model=List[QueueEntryResponse],
)
async def get_doctor_queue(
    doctor_id: UUID,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    service: QueueService = Depends(get_queue_service)
):
    """Get the ordered queue for a doctor on a specific date"""
    queue = await service.get_queue_for_doctor(doctor_id, date)
    return queue
