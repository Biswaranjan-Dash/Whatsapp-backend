# Quick Start Guide

## 🚀 3-Minute Setup (Docker)

### Step 1: Start Services
```powershell
docker-compose up -d
```

This starts:
- PostgreSQL database
- FastAPI application (with auto-migrations)
- pgAdmin (optional database viewer)

### Step 2: Verify
Visit http://localhost:8000/docs - you should see the OpenAPI documentation.

### Step 3: Test the API

**Create a patient:**
```powershell
curl -X POST http://localhost:8000/api/v1/patients `
  -H "Content-Type: application/json" `
  -d '{"first_name":"John","last_name":"Doe","phone":"+919876543210","age":30}'
```

**Create a doctor:**
```powershell
curl -X POST http://localhost:8000/api/v1/doctors `
  -H "Content-Type: application/json" `
  -d '{"name":"Dr. Smith","code":"DR_SMITH"}'
```

Done! 🎉

---

## 🔧 Local Development Setup (Without Docker)

### Step 1: Install PostgreSQL
Download and install PostgreSQL 16 from https://www.postgresql.org/download/

### Step 2: Create Database
```powershell
psql -U postgres
CREATE DATABASE appointment_db;
\q
```

### Step 3: Setup Python Environment
```powershell
# Run the setup script
.\setup.ps1

# Or manually:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 4: Configure Environment
Edit `.env` file with your database credentials:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/appointment_db
DATABASE_URL_SYNC=postgresql://postgres:yourpassword@localhost:5432/appointment_db
```

### Step 5: Run Migrations
```powershell
alembic upgrade head
```

### Step 6: Start the API
```powershell
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs

---

## 🧪 Running Tests

### Setup Test Database
```powershell
# Start PostgreSQL (via Docker)
docker-compose up -d postgres

# Create test database
docker exec -it clinic_postgres psql -U postgres -c "CREATE DATABASE clinic_test_db;"
```

### Run All Tests
```powershell
pytest tests/integration/ -v
```

### Run Specific Test Suites
```powershell
# Basic flows (patients, doctors, availability)
pytest tests/integration/test_basic_flows.py -v

# Appointment booking (including capacity enforcement)
pytest tests/integration/test_appointments.py -v

# Concurrency test (CRITICAL - 30 concurrent bookings)
pytest tests/integration/test_appointments.py::TestConcurrentBooking -v

# Check-in flow
pytest tests/integration/test_checkin.py -v
```

---

## 📊 Viewing the Database

### Option 1: pgAdmin (via Docker)
1. Visit http://localhost:5050
2. Login: `admin@clinic.local` / `admin`
3. Add server:
   - Host: `postgres`
   - Port: `5432`
   - Username: `postgres`
   - Password: `postgres`

### Option 2: psql Command Line
```powershell
docker exec -it clinic_postgres psql -U postgres -d appointment_db
```

Useful queries:
```sql
-- View all tables
\dt

-- Check appointments
SELECT * FROM appointments;

-- Check capacity
SELECT * FROM doctor_daily_capacities;

-- View queue
SELECT * FROM queue_entries ORDER BY position;
```

---

## 🐛 Troubleshooting

### Port Already in Use
If port 8000 or 5432 is already in use:

**Option 1:** Stop conflicting services
```powershell
docker ps  # Find conflicting containers
docker stop <container-id>
```

**Option 2:** Change ports in `docker-compose.yml`
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Database Connection Errors
```powershell
# Check if PostgreSQL is running
docker ps | findstr postgres

# View PostgreSQL logs
docker logs clinic_postgres

# Restart database
docker-compose restart postgres
```

### Migration Errors
```powershell
# Check current migration status
alembic current

# View migration history
alembic history

# Reset database (CAUTION: deletes all data)
docker-compose down -v
docker-compose up -d
```

---

## 📚 API Testing with curl

### Windows PowerShell Examples

**Get health status:**
```powershell
curl http://localhost:8000/health
```

**Create patient:**
```powershell
$body = @{
    first_name = "Alice"
    last_name = "Johnson"
    phone = "+919876543210"
    age = 28
    email = "alice@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/patients" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

**List doctors:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/doctors" -Method Get
```

**Book appointment:**
```powershell
$booking = @{
    patient_id = "your-patient-uuid"
    doctor_id = "your-doctor-uuid"
    date = "2025-11-15"
    idempotency_key = "booking-123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/appointments" `
    -Method Post `
    -Body $booking `
    -ContentType "application/json"
```

---

## 🎯 Next Steps

1. ✅ API running? Visit http://localhost:8000/docs
2. ✅ Tests passing? Run `pytest tests/integration/ -v`
3. ✅ Ready for development? Check the [README.md](README.md) for architecture details

Happy coding! 🚀
