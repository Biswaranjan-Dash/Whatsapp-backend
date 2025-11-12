import asyncio
from datetime import date
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.models import Base
from app.db.session import get_db

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinic_test_db"

async def test():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create doctor
        doctor_resp = await client.post("/api/v1/doctors", json={"name": "Dr. Test", "code": "TEST", "specialty": "General"})
        doctor = doctor_resp.json()
        
        # Set availability
        today = date.today()
        await client.post(f"/api/v1/doctors/{doctor['id']}/availability", json={"date": today.isoformat(), "is_present": True})
        
        # Create patient
        patient_resp = await client.post("/api/v1/patients", json={"first_name": "Test", "phone": "+919999999999"})
        patient = patient_resp.json()
        
        # Book appointment
        appt_resp = await client.post("/api/v1/appointments", json={"patient_id": patient["id"], "doctor_id": doctor["id"], "date": today.isoformat()})
        appointment = appt_resp.json()
        
        # First check-in
        checkin_data = {"appointment_id": appointment["id"], "patient_id": patient["id"]}
        response1 = await client.post("/api/v1/checkins", json=checkin_data)
        print(f"First check-in: {response1.status_code}")
        
        # Second check-in (duplicate)
        response2 = await client.post("/api/v1/checkins", json=checkin_data)
        print(f"Second check-in status: {response2.status_code}")
        print(f"Second check-in body: {response2.json()}")
    
    await engine.dispose()

asyncio.run(test())
