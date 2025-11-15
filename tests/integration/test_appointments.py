import pytest
import asyncio
from datetime import date
from uuid import uuid4


@pytest.mark.asyncio
class TestAppointmentBooking:
    """Test appointment booking with capacity enforcement"""
    
    async def test_book_appointment_success(self, client, test_patient, test_doctor_with_availability):
        """Test successful appointment booking"""
        today = date.today()
        
        response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat(),
                "idempotency_key": "test-key-001"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == test_patient["id"]
        assert data["doctor_id"] == test_doctor_with_availability["id"]
        assert data["slot"] == 1
        assert data["status"] == "booked"
        assert "id" in data
    
    async def test_book_appointment_without_setting_availability(self, client, test_patient, test_doctor):
        """Test that doctors are available by default without explicit availability setting"""
        today = date.today()
        
        # Book appointment without setting availability first
        response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor["id"],
                "date": today.isoformat()
            }
        )
        
        # Should succeed because doctors are available by default
        assert response.status_code == 201
        data = response.json()
        assert data["slot"] == 1
    
    async def test_book_appointment_idempotency(self, client, test_patient, test_doctor_with_availability):
        """Test idempotent booking - same key returns same appointment"""
        today = date.today()
        idempotency_key = f"idempotent-{uuid4()}"
        
        booking_data = {
            "patient_id": test_patient["id"],
            "doctor_id": test_doctor_with_availability["id"],
            "date": today.isoformat(),
            "idempotency_key": idempotency_key
        }
        
        response1 = await client.post("/api/v1/appointments", json=booking_data)
        assert response1.status_code == 201
        appt1 = response1.json()
        
        response2 = await client.post("/api/v1/appointments", json=booking_data)
        assert response2.status_code == 201
        appt2 = response2.json()
        
        assert appt1["id"] == appt2["id"]
        assert appt1["slot"] == appt2["slot"]
    
    async def test_book_appointment_without_availability(self, client, test_patient, test_doctor):
        """Test booking fails when doctor availability is marked absent"""
        today = date.today()
        
        await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": today.isoformat(),
                "is_present": False,
                "notes": "Doctor on leave"
            }
        )
        
        response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor["id"],
                "date": today.isoformat()
            }
        )
        
        assert response.status_code == 422
        assert "not available" in response.json()["detail"]["message"].lower()
    
    async def test_book_appointment_nonexistent_doctor(self, client, test_patient):
        """Test booking with non-existent doctor fails"""
        today = date.today()
        fake_doctor_id = str(uuid4())
        
        response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": fake_doctor_id,
                "date": today.isoformat()
            }
        )
        
        assert response.status_code == 404
    
    async def test_get_appointment(self, client, test_patient, test_doctor_with_availability):
        """Test retrieving appointment by ID"""
        today = date.today()
        
        response1 = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        appt = response1.json()
        
        response2 = await client.get(f"/api/v1/appointments/{appt['id']}")
        
        assert response2.status_code == 200
        data = response2.json()
        assert data["id"] == appt["id"]
    
    async def test_list_doctor_appointments(self, client, test_patient, test_doctor_with_availability):
        """Test listing appointments for a doctor on a specific date"""
        today = date.today()
        
        await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        
        response = await client.get(
            f"/api/v1/appointments/doctors/{test_doctor_with_availability['id']}/appointments",
            params={"date": today.isoformat()}
        )
        
        assert response.status_code == 200
        appointments = response.json()
        assert len(appointments) >= 1
        assert appointments[0]["doctor_id"] == test_doctor_with_availability["id"]


@pytest.mark.asyncio
class TestCapacityEnforcement:
    """Test max 10 appointments per doctor per day"""
    
    async def test_book_10_appointments_success(self, client, test_doctor_with_availability):
        """Test booking exactly 10 appointments succeeds"""
        today = date.today()
        
        for i in range(10):
            patient_response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"Patient{i}",
                    "phone": f"+9191234567{i:02d}"
                }
            )
            patient = patient_response.json()
            
            appt_response = await client.post(
                "/api/v1/appointments",
                json={
                    "patient_id": patient["id"],
                    "doctor_id": test_doctor_with_availability["id"],
                    "date": today.isoformat()
                }
            )
            
            assert appt_response.status_code == 201
            appt_data = appt_response.json()
            assert appt_data["slot"] == i + 1
    
    async def test_11th_appointment_fails(self, client, test_doctor_with_availability):
        """Test booking 11th appointment fails (capacity full)"""
        today = date.today()
        
        for i in range(10):
            patient_response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"Patient{i}",
                    "phone": f"+9191234560{i:02d}"
                }
            )
            patient = patient_response.json()
            
            await client.post(
                "/api/v1/appointments",
                json={
                    "patient_id": patient["id"],
                    "doctor_id": test_doctor_with_availability["id"],
                    "date": today.isoformat()
                }
            )
        
        patient_11 = await client.post(
            "/api/v1/patients",
            json={"first_name": "Patient11", "phone": "+919999999999"}
        )
        
        response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": patient_11.json()["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        
        assert response.status_code == 409
        assert "no available slots" in response.json()["detail"]["message"].lower()


@pytest.mark.asyncio
class TestConcurrentBooking:
    """Test concurrent booking safety - CRITICAL TEST"""
    
    async def test_30_concurrent_bookings_only_10_succeed(self, client, test_doctor_with_availability):
        """
        Test concurrency safety: 
        Spawn 30 concurrent booking attempts, exactly 10 should succeed.
        """
        today = date.today()
        
        patients = []
        for i in range(30):
            response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"ConcurrentPatient{i}",
                    "phone": f"+9198765432{i:02d}"
                }
            )
            patients.append(response.json())
        
        async def book_appointment(patient_id, index):
            """Book appointment for a patient"""
            response = await client.post(
                "/api/v1/appointments",
                json={
                    "patient_id": patient_id,
                    "doctor_id": test_doctor_with_availability["id"],
                    "date": today.isoformat()
                }
            )
            return {"index": index, "status": response.status_code, "data": response.json()}
        
        results = await asyncio.gather(
            *[book_appointment(p["id"], i) for i, p in enumerate(patients)],
            return_exceptions=True
        )
        
        successes = [r for r in results if not isinstance(r, Exception) and r["status"] == 201]
        failures = [r for r in results if not isinstance(r, Exception) and r["status"] != 201]
        
        assert len(successes) == 10, f"Expected exactly 10 successful bookings, got {len(successes)}"
        assert len(failures) == 20, f"Expected exactly 20 failed bookings, got {len(failures)}"
        
        slots = [s["data"]["slot"] for s in successes]
        assert sorted(slots) == list(range(1, 11)), "Slots should be 1-10"
        assert len(set(slots)) == 10, "All slots should be unique"
        
        for failure in failures:
            assert failure["status"] == 409
            assert "no available slots" in failure["data"]["detail"]["message"].lower() or "capacity full" in failure["data"]["detail"]["message"].lower()
