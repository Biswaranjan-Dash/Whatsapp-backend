"""
Test to demonstrate the new default availability behavior
"""
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
        print("1. Creating doctor...")
        doctor_resp = await client.post("/api/v1/doctors", json={
            "name": "Dr. Available", 
            "code": "AVAIL_001", 
            "specialty": "General"
        })
        doctor = doctor_resp.json()
        print(f"   ✓ Doctor created: {doctor['name']}")
        
        # Create patient
        print("\n2. Creating patient...")
        patient_resp = await client.post("/api/v1/patients", json={
            "first_name": "John",
            "last_name": "Doe", 
            "phone": "+919999999999"
        })
        patient = patient_resp.json()
        print(f"   ✓ Patient created: {patient['first_name']} {patient['last_name']}")
        
        # Book appointment WITHOUT setting availability first
        today = date.today()
        print(f"\n3. Booking appointment for {today} WITHOUT setting availability...")
        appt_resp = await client.post("/api/v1/appointments", json={
            "patient_id": patient["id"], 
            "doctor_id": doctor["id"], 
            "date": today.isoformat()
        })
        print(f"   Status: {appt_resp.status_code}")
        if appt_resp.status_code == 201:
            appointment = appt_resp.json()
            print(f"   ✓ SUCCESS! Appointment booked with slot {appointment['slot']}")
            print(f"   → This proves doctors are AVAILABLE BY DEFAULT")
        else:
            print(f"   ✗ FAILED: {appt_resp.json()}")
        
        # Now mark doctor as unavailable for tomorrow
        from datetime import timedelta
        tomorrow = today + timedelta(days=1)
        print(f"\n4. Marking doctor as UNAVAILABLE for {tomorrow}...")
        avail_resp = await client.post(f"/api/v1/doctors/{doctor['id']}/availability", json={
            "date": tomorrow.isoformat(),
            "is_present": False,
            "notes": "Doctor on leave"
        })
        print(f"   ✓ Availability set to False")
        
        # Try to book for tomorrow
        print(f"\n5. Trying to book appointment for {tomorrow}...")
        appt2_resp = await client.post("/api/v1/appointments", json={
            "patient_id": patient["id"],
            "doctor_id": doctor["id"],
            "date": tomorrow.isoformat()
        })
        print(f"   Status: {appt2_resp.status_code}")
        if appt2_resp.status_code != 201:
            error = appt2_resp.json()
            print(f"   ✓ SUCCESS! Booking blocked as expected")
            print(f"   → Reason: {error['detail']['message']}")
        else:
            print(f"   ✗ UNEXPECTED: Booking should have failed!")
    
    await engine.dispose()

print("=" * 70)
print("TESTING NEW AVAILABILITY BEHAVIOR")
print("=" * 70)
asyncio.run(test())
print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
