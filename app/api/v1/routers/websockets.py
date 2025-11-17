from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from typing import Dict, Set, Optional
import json
from uuid import UUID
from app.db.session import get_db
from app.repositories.queue_repo import QueueRepository
from app.repositories.appointment_repo import AppointmentRepository
from app.repositories.doctor_repo import DoctorRepository
from app.repositories.patient_repo import PatientRepository
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["websockets"])


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        # Map of date -> set of websockets subscribed to that date
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of websocket -> subscribed date
        self.subscriptions: Dict[WebSocket, str] = {}
    
    def subscribe(self, websocket: WebSocket, date_key: str):
        """Subscribe a websocket to a date (websocket should already be accepted)"""
        # Remove from old subscription if exists
        if websocket in self.subscriptions:
            old_date = self.subscriptions[websocket]
            if old_date in self.active_connections:
                self.active_connections[old_date].discard(websocket)
        
        # Add to new subscription
        if date_key not in self.active_connections:
            self.active_connections[date_key] = set()
        
        self.active_connections[date_key].add(websocket)
        self.subscriptions[websocket] = date_key
        
        logger.info(
            "WebSocket subscribed",
            date=date_key,
            total_connections=len(self.active_connections.get(date_key, []))
        )
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket"""
        if websocket in self.subscriptions:
            date_key = self.subscriptions[websocket]
            
            if date_key in self.active_connections:
                self.active_connections[date_key].discard(websocket)
                
                # Clean up empty date subscriptions
                if not self.active_connections[date_key]:
                    del self.active_connections[date_key]
            
            del self.subscriptions[websocket]
            
            logger.info("WebSocket disconnected", date=date_key)
    
    async def broadcast_to_date(self, date_key: str, message: dict):
        """Broadcast a message to all connections subscribed to a date"""
        if date_key not in self.active_connections:
            return
        
        disconnected = []
        
        for websocket in self.active_connections[date_key]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error("Failed to send message", error=str(e))
                disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.disconnect(ws)


# Global connection manager instance
manager = ConnectionManager()


async def get_queue_data(
    db: AsyncSession,
    target_date: date
) -> dict:
    """Get complete queue data for ALL doctors on a specific date"""
    queue_repo = QueueRepository(db)
    appointment_repo = AppointmentRepository(db)
    patient_repo = PatientRepository(db)
    doctor_repo = DoctorRepository(db)
    
    # Get ALL appointments for the date (across all doctors)
    appointments = await appointment_repo.list_by_date(target_date)
    
    if not appointments:
        return {
            "date": target_date.isoformat(),
            "total_appointments": 0,
            "total_doctors": 0,
            "doctors": [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Group appointments by doctor
    doctors_data = {}
    
    for appt in appointments:
        doctor_id = appt.doctor_id
        
        # Get doctor info if not already fetched
        if doctor_id not in doctors_data:
            doctor = await doctor_repo.get_by_id(doctor_id)
            if not doctor:
                continue
            
            doctors_data[doctor_id] = {
                "doctor": {
                    "id": str(doctor.id),
                    "name": doctor.name,
                    "code": doctor.code,
                    "specialty": doctor.specialty
                },
                "appointments": []
            }
        
        # Get patient info
        patient = await patient_repo.get_by_id(appt.patient_id)
        
        # Get queue entry if exists
        queue_entries = await queue_repo.list_by_doctor_date(doctor_id, target_date)
        queue_entry = next(
            (q for q in queue_entries if q.appointment_id == appt.id),
            None
        )
        
        # Add appointment to doctor's list
        doctors_data[doctor_id]["appointments"].append({
            "appointment_id": str(appt.id),
            "slot": appt.slot,
            "status": appt.status.value,
            "patient": {
                "id": str(patient.id),
                "name": patient.name,
                "phone": patient.phone,
                "age": patient.age,
                "gender": patient.gender
            } if patient else None,
            "queue": {
                "position": queue_entry.position,
                "checked_in_at": queue_entry.checked_in_at.isoformat() if queue_entry.checked_in_at else None,
                "status": queue_entry.status.value
            } if queue_entry else None
        })
    
    # Sort each doctor's appointments by slot
    for doctor_data in doctors_data.values():
        doctor_data["appointments"].sort(key=lambda x: x["slot"])
        doctor_data["total_appointments"] = len(doctor_data["appointments"])
        
        # Calculate checked-in count
        doctor_data["checked_in_count"] = sum(
            1 for appt in doctor_data["appointments"] 
            if appt["queue"] and appt["queue"]["status"] == "checked_in"
        )
    
    # Convert to list and sort by doctor name
    doctors_list = list(doctors_data.values())
    doctors_list.sort(key=lambda x: x["doctor"]["name"])
    
    return {
        "date": target_date.isoformat(),
        "total_appointments": len(appointments),
        "total_doctors": len(doctors_list),
        "doctors": doctors_list,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.websocket("/ws/queue")
async def websocket_queue(websocket: WebSocket):
    """
    WebSocket endpoint for real-time queue updates across ALL doctors.
    
    Client sends: {"action": "subscribe", "date": "2025-11-17"}
    Server responds with: full queue data for all doctors and real-time updates
    """
    await websocket.accept()
    subscribed_date: Optional[str] = None
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "subscribe":
                target_date_str = message.get("date")
                
                if not target_date_str:
                    await websocket.send_json({
                        "error": "Missing 'date' field in subscribe message"
                    })
                    continue
                
                try:
                    target_date = date.fromisoformat(target_date_str)
                except ValueError:
                    await websocket.send_json({
                        "error": "Invalid date format. Use YYYY-MM-DD"
                    })
                    continue
                
                # Update subscription (use date only as key, no doctor_id)
                date_key = target_date_str
                manager.subscribe(websocket, date_key)
                subscribed_date = date_key
                
                # Send initial queue data for ALL doctors
                # Create a new database session for this operation
                from app.db.session import AsyncSessionLocal
                async with AsyncSessionLocal() as db:
                    queue_data = await get_queue_data(db, target_date)
                    await websocket.send_json({
                        "type": "snapshot",
                        "data": queue_data
                    })
                    logger.info(
                        "Client subscribed to central queue",
                        date=target_date_str
                    )
            
            elif action == "unsubscribe":
                if subscribed_date:
                    manager.disconnect(websocket)
                    subscribed_date = None
                    
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "message": "Successfully unsubscribed"
                    })
            
            elif action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            else:
                await websocket.send_json({
                    "error": f"Unknown action: {action}"
                })
    
    except WebSocketDisconnect:
        if subscribed_date:
            manager.disconnect(websocket)
        logger.info("Client disconnected from central queue")
    
    except json.JSONDecodeError:
        await websocket.send_json({
            "error": "Invalid JSON message"
        })
    
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        if subscribed_date:
            manager.disconnect(websocket)


async def notify_queue_update(doctor_id: UUID, target_date: date, db: AsyncSession):
    """
    Helper function to notify all subscribers of a queue update.
    Call this after check-in, appointment booking, or status changes.
    Broadcasts to all clients subscribed to the date (regardless of doctor).
    """
    date_key = target_date.isoformat()
    queue_data = await get_queue_data(db, target_date)
    
    await manager.broadcast_to_date(date_key, {
        "type": "update",
        "data": queue_data
    })
    
    logger.info(
        "Queue update broadcasted",
        date=str(target_date),
        subscribers=len(manager.active_connections.get(date_key, []))
    )
