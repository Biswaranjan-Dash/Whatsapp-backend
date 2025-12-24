from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from datetime import date
from typing import List
from app.schemas import (
    DoctorCreate, DoctorResponse, AvailabilityUpsert, 
    AvailabilityResponse, ErrorResponse
)
from app.services.doctor_service import DoctorService
from app.api.v1.deps import get_doctor_service
from app.core.logging import get_logger

router = APIRouter(prefix="/doctors", tags=["doctors"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_doctor(
    doctor_data: DoctorCreate,
    service: DoctorService = Depends(get_doctor_service)
):
    """Create a new doctor"""
    try:
        doctor = await service.create_doctor(doctor_data.model_dump())
        return doctor
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)}
        )
    except Exception as e:
        logger.error("Failed to create doctor", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalError", "message": "Failed to create doctor"}
        )


@router.get(
    "",
    response_model=List[DoctorResponse],
)
async def list_doctors(
    date: date = Query(None, description="Include availability for this date"),
    service: DoctorService = Depends(get_doctor_service)
):
    """List all doctors, optionally with availability for a specific date"""
    if date:
        doctors_with_availability = await service.list_doctors_with_availability(date)
        # Return doctors with availability info embedded
        return [
            {
                **doctor["doctor"].__dict__,
                "is_available": doctor["is_available"]
            }
            for doctor in doctors_with_availability
        ]
    else:
        doctors = await service.list_doctors()
        return doctors


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_doctor(
    doctor_id: UUID,
    service: DoctorService = Depends(get_doctor_service)
):
    """Get doctor by ID"""
    doctor = await service.get_doctor(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Doctor {doctor_id} not found"}
        )
    return doctor


@router.post(
    "/{doctor_id}/availability",
    response_model=AvailabilityResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}}
)
async def set_availability(
    doctor_id: UUID,
    availability_data: AvailabilityUpsert,
    service: DoctorService = Depends(get_doctor_service)
):
    """Set or update doctor availability for a specific date"""
    try:
        availability = await service.upsert_availability(
            doctor_id,
            availability_data.date,
            availability_data.is_present,
            availability_data.notes
        )
        return availability
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": str(e)}
        )


@router.get(
    "/{doctor_id}/availability",
    response_model=AvailabilityResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_availability(
    doctor_id: UUID,
    date: date = Query(..., description="Date in YYYY-MM-DD format"),
    service: DoctorService = Depends(get_doctor_service)
):
    """
    Get doctor availability for a specific date.
    Returns available by default if no record exists.
    """
    # First verify doctor exists
    doctor = await service.get_doctor(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": f"Doctor {doctor_id} not found"
            }
        )
    
    availability = await service.get_availability(doctor_id, date)
    
    # If no availability record exists, doctor is available by default
    if not availability:
        from datetime import datetime
        return {
            "id": None,
            "doctor_id": str(doctor_id),
            "date": date.isoformat(),
            "is_present": True,
            "notes": "Available (default)",
            "updated_by": None,
            "updated_at": None
        }
    
    return availability
