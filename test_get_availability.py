"""
Test the GET availability endpoint with the new default behavior
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
            "name": "Dr. Test", 
            "code": "TEST_001", 
            "specialty": "General"
        })
        doctor = doctor_resp.json()
        doctor_id = doctor['id']
        print(f"   ✓ Doctor created: {doctor['name']}")
        
        # Get availability WITHOUT setting it first
        today = date.today()
        print(f"\n2. Getting availability for {today} WITHOUT setting it...")
        avail_resp = await client.get(f"/api/v1/doctors/{doctor_id}/availability?date={today}")
        print(f"   Status: {avail_resp.status_code}")
        if avail_resp.status_code == 200:
            availability = avail_resp.json()
            print(f"   ✓ SUCCESS!")
            print(f"   → is_present: {availability['is_present']}")
            print(f"   → notes: {availability['notes']}")
        else:
            print(f"   ✗ FAILED: {avail_resp.json()}")
        
        # Now set availability to FALSE (unavailable)
        from datetime import timedelta
        tomorrow = today + timedelta(days=1)
        print(f"\n3. Setting availability to FALSE for {tomorrow}...")
        set_resp = await client.post(f"/api/v1/doctors/{doctor_id}/availability", json={
            "date": tomorrow.isoformat(),
            "is_present": False,
            "notes": "Doctor on leave"
        })
        print(f"   ✓ Availability set")
        
        # Get the unavailable day
        print(f"\n4. Getting availability for {tomorrow}...")
        avail2_resp = await client.get(f"/api/v1/doctors/{doctor_id}/availability?date={tomorrow}")
        print(f"   Status: {avail2_resp.status_code}")
        if avail2_resp.status_code == 200:
            availability2 = avail2_resp.json()
            print(f"   ✓ Response received")
            print(f"   → is_present: {availability2['is_present']}")
            print(f"   → notes: {availability2['notes']}")
        
        # Test with non-existent doctor
        print(f"\n5. Testing with non-existent doctor...")
        fake_id = "00000000-0000-0000-0000-000000000000"
        fake_resp = await client.get(f"/api/v1/doctors/{fake_id}/availability?date={today}")
        print(f"   Status: {fake_resp.status_code}")
        if fake_resp.status_code == 404:
            error = fake_resp.json()
            print(f"   ✓ Correctly returns 404")
            print(f"   → Error: {error['detail']['message']}")
    
    await engine.dispose()

print("=" * 70)
print("TESTING GET AVAILABILITY ENDPOINT")
print("=" * 70)
asyncio.run(test())
print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
