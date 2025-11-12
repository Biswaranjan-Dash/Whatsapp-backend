import pytest
from datetime import date
from uuid import uuid4


@pytest.mark.asyncio
class TestCheckInFlow:
    """Test patient check-in and queue management"""
    
    async def test_check_in_success(self, client, test_patient, test_doctor_with_availability):
        """Test successful check-in"""
        today = date.today()
        
        appt_response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        appointment = appt_response.json()
        
        checkin_response = await client.post(
            "/api/v1/checkins",
            json={
                "appointment_id": appointment["id"],
                "patient_id": test_patient["id"]
            }
        )
        
        assert checkin_response.status_code == 201
        data = checkin_response.json()
        assert data["queue_position"] == 1
        assert data["appointment_id"] == appointment["id"]
        assert "checked_in_at" in data
    
    async def test_check_in_assigns_positions_in_order(self, client, test_doctor_with_availability):
        """Test check-in assigns queue positions in checked-in order"""
        today = date.today()
        
        patients_and_appointments = []
        for i in range(3):
            patient_response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"QueuePatient{i}",
                    "phone": f"+919000000{i:03d}"
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
            appointment = appt_response.json()
            patients_and_appointments.append((patient, appointment))
        
        checkin_results = []
        for patient, appointment in patients_and_appointments:
            checkin_response = await client.post(
                "/api/v1/checkins",
                json={
                    "appointment_id": appointment["id"],
                    "patient_id": patient["id"]
                }
            )
            assert checkin_response.status_code == 201
            checkin_results.append(checkin_response.json())
        
        assert checkin_results[0]["queue_position"] == 1
        assert checkin_results[1]["queue_position"] == 2
        assert checkin_results[2]["queue_position"] == 3
    
    async def test_check_in_duplicate_fails(self, client, test_patient, test_doctor_with_availability):
        """Test duplicate check-in returns 409"""
        today = date.today()
        
        appt_response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        appointment = appt_response.json()
        
        checkin_data = {
            "appointment_id": appointment["id"],
            "patient_id": test_patient["id"]
        }
        
        response1 = await client.post("/api/v1/checkins", json=checkin_data)
        assert response1.status_code == 201
        
        response2 = await client.post("/api/v1/checkins", json=checkin_data)
        assert response2.status_code == 409
        msg = response2.json()["detail"]["message"].lower()
        assert "already" in msg and "checked" in msg
    
    async def test_check_in_wrong_patient_fails(self, client, test_doctor_with_availability):
        """Test check-in with wrong patient ID fails"""
        today = date.today()
        
        patient1_response = await client.post(
            "/api/v1/patients",
            json={"first_name": "Patient1", "phone": "+919111111111"}
        )
        patient1 = patient1_response.json()
        
        patient2_response = await client.post(
            "/api/v1/patients",
            json={"first_name": "Patient2", "phone": "+919222222222"}
        )
        patient2 = patient2_response.json()
        
        appt_response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": patient1["id"],
                "doctor_id": test_doctor_with_availability["id"],
                "date": today.isoformat()
            }
        )
        appointment = appt_response.json()
        
        response = await client.post(
            "/api/v1/checkins",
            json={
                "appointment_id": appointment["id"],
                "patient_id": patient2["id"]
            }
        )
        
        assert response.status_code == 400
        assert "does not belong" in response.json()["detail"]["message"].lower()
    
    async def test_check_in_nonexistent_appointment(self, client, test_patient):
        """Test check-in with non-existent appointment fails"""
        fake_appointment_id = str(uuid4())
        
        response = await client.post(
            "/api/v1/checkins",
            json={
                "appointment_id": fake_appointment_id,
                "patient_id": test_patient["id"]
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]["message"].lower()
    
    async def test_get_doctor_queue(self, client, test_doctor_with_availability):
        """Test retrieving doctor's queue for a date"""
        today = date.today()
        
        for i in range(2):
            patient_response = await client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"QueueTest{i}",
                    "phone": f"+919333333{i:03d}"
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
            appointment = appt_response.json()
            
            await client.post(
                "/api/v1/checkins",
                json={
                    "appointment_id": appointment["id"],
                    "patient_id": patient["id"]
                }
            )
        
        response = await client.get(
            f"/api/v1/checkins/doctors/{test_doctor_with_availability['id']}/queue",
            params={"date": today.isoformat()}
        )
        
        assert response.status_code == 200
        queue = response.json()
        assert len(queue) >= 2
        
        positions = [entry["position"] for entry in queue]
        assert positions == sorted(positions), "Queue should be ordered by position"


@pytest.mark.asyncio
class TestCheckInDateValidation:
    """Test check-in date validation"""
    
    async def test_check_in_future_date_fails(self, client, test_patient, test_doctor):
        """Test check-in for future appointment fails"""
        from datetime import timedelta
        tomorrow = date.today() + timedelta(days=1)
        
        await client.post(
            f"/api/v1/doctors/{test_doctor['id']}/availability",
            json={
                "date": tomorrow.isoformat(),
                "is_present": True
            }
        )
        
        appt_response = await client.post(
            "/api/v1/appointments",
            json={
                "patient_id": test_patient["id"],
                "doctor_id": test_doctor["id"],
                "date": tomorrow.isoformat()
            }
        )
        appointment = appt_response.json()
        
        response = await client.post(
            "/api/v1/checkins",
            json={
                "appointment_id": appointment["id"],
                "patient_id": test_patient["id"]
            }
        )
        
        assert response.status_code == 422
        assert "only allowed on appointment date" in response.json()["detail"]["message"].lower()
