import pytest
import asyncio
from datetime import date
from uuid import uuid4


@pytest.mark.asyncio
class TestPatientFlow:
    """Test patient registration flow"""
    
    async def test_create_patient(self, client):
        """Test creating a new patient"""
        response = await client.post(
            "/api/v1/patients",
            json={
                "name": "Alice Johnson",
                "age": 25,
                "gender": "female",
                "phone": "+919123456789",
                "email": "alice@example.com"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice Johnson"
        assert data["age"] == 25
        assert data["gender"] == "female"
        assert data["phone"] == "+919123456789"
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_patient_duplicate_phone(self, client):
        """Test creating patient with duplicate phone returns existing"""
        patient_data = {
            "name": "Bob Smith",
            "age": 40,
            "gender": "male",
            "phone": "+919998887777",
            "email": "bob@example.com"
        }
        
        response1 = await client.post("/api/v1/patients", json=patient_data)
        assert response1.status_code == 201
        patient1 = response1.json()
        
        response2 = await client.post("/api/v1/patients", json=patient_data)
        assert response2.status_code == 201
        patient2 = response2.json()
        
        assert patient1["id"] == patient2["id"]
    
    async def test_get_patient(self, client, test_patient):
        """Test retrieving a patient by ID"""
        response = await client.get(f"/api/v1/patients/{test_patient['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_patient["id"]
        assert data["name"] == test_patient["name"]
    
    async def test_get_nonexistent_patient(self, client):
        """Test retrieving non-existent patient returns 404"""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/patients/{fake_id}")
        
        assert response.status_code == 404
        assert "NotFound" in response.json()["detail"]["error"]


@pytest.mark.asyncio
class TestDoctorFlow:
    """Test doctor management flow"""
    
    async def test_create_doctor(self, client):
        """Test creating a new doctor"""
        response = await client.post(
            "/api/v1/doctors",
            json={
                "name": "Dr. Williams",
                "code": "DR_WILL_001",
                "specialty": "Cardiology"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dr. Williams"
        assert data["code"] == "DR_WILL_001"
        assert data["specialty"] == "Cardiology"
        assert "id" in data
    
    async def test_create_doctor_duplicate_code(self, client, test_doctor):
        """Test creating doctor with duplicate code fails"""
        response = await client.post(
            "/api/v1/doctors",
            json={
                "name": "Dr. Duplicate",
                "code": test_doctor["code"],
                "specialty": "Surgery"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]["message"]
    
    async def test_list_doctors(self, client, test_doctor):
        """Test listing all doctors"""
        response = await client.get("/api/v1/doctors")
        
        assert response.status_code == 200
        doctors = response.json()
        assert len(doctors) >= 1
        assert any(d["id"] == test_doctor["id"] for d in doctors)
    
    async def test_get_doctor(self, client, test_doctor):
        """Test retrieving a doctor by ID"""
        response = await client.get(f"/api/v1/doctors/{test_doctor['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_doctor["id"]
        assert data["name"] == test_doctor["name"]


@pytest.mark.asyncio
class TestAvailabilityFlow:
    """Test doctor availability management"""
    
    async def test_set_availability(self, client, test_doctor):
        """Test setting doctor availability"""
        today = date.today()
        response = await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": today.isoformat(),
                "is_present": True,
                "notes": "Morning shift"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["doctor_id"] == test_doctor["id"]
        assert data["is_present"] is True
        assert data["notes"] == "Morning shift"
    
    async def test_update_availability(self, client, test_doctor):
        """Test updating doctor availability (upsert)"""
        today = date.today()
        
        response1 = await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": today.isoformat(),
                "is_present": True,
                "notes": "Morning"
            }
        )
        assert response1.status_code == 200
        avail1 = response1.json()
        
        response2 = await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": today.isoformat(),
                "is_present": False,
                "notes": "On leave"
            }
        )
        assert response2.status_code == 200
        avail2 = response2.json()
        
        assert avail1["id"] == avail2["id"]
        assert avail2["is_present"] is False
        assert avail2["notes"] == "On leave"
    
    async def test_get_availability(self, client, test_doctor):
        """Test retrieving doctor availability"""
        today = date.today()
        
        await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": today.isoformat(),
                "is_present": True
            }
        )
        
        response = await client.get(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            params={"date": today.isoformat()}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_present"] is True
