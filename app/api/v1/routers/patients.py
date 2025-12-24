from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional
from app.schemas import PatientCreate, PatientResponse, ErrorResponse
from app.services.patient_service import PatientService
from app.api.v1.deps import get_patient_service
from app.core.logging import get_logger

router = APIRouter(prefix="/patients", tags=["patients"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}}
)
async def create_patient(
    patient_data: PatientCreate,
    service: PatientService = Depends(get_patient_service)
):
    """Create a new patient or return existing patient with same phone"""
    try:
        patient = await service.create_patient(patient_data.model_dump())
        return patient
    except Exception as e:
        logger.error("Failed to create patient", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)}
        )


@router.get(
    "/search",
    response_model=Optional[PatientResponse],
    responses={400: {"model": ErrorResponse}}
)
async def search_patient(
    phone: str = Query(..., description="Phone number to search"),
    service: PatientService = Depends(get_patient_service)
):
    """Search for patient by phone number"""
    try:
        # Normalize phone number
        import re
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        patient = await service.get_patient_by_phone(cleaned_phone)
        return patient
    except Exception as e:
        logger.error("Failed to search patient", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "SearchError", "message": str(e)}
        )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_patient(
    patient_id: UUID,
    service: PatientService = Depends(get_patient_service)
):
    """Get patient by ID"""
    patient = await service.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Patient {patient_id} not found"}
        )
    return patient
