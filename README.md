# Medical Appointment Booking API

Production-quality FastAPI service implementing patient registration, doctor scheduling, appointment booking, and check-in queue management with **concurrency-safe booking** and **idempotent operations**.

## 🚀 Features

- **Patient Management**: Register patients with phone normalization and de-duplication
- **Doctor Management**: Manage doctors and their daily availability
- **Appointment Booking**: 
  - Max 10 appointments per doctor per day (enforced atomically)
  - Concurrency-safe slot allocation
  - Idempotent booking via `idempotency_key`
  - Doctor availability validation
- **Check-in Queue**: 
  - Atomic queue position assignment
  - Check-in only allowed on appointment date
  - Ordered queue management
- **Production Ready**:
  - Async FastAPI with SQLAlchemy async ORM
  - PostgreSQL with proper indexes and constraints
  - Docker Compose for reproducible environment
  - Comprehensive integration tests including concurrency tests
  - Structured JSON logging with PHI redaction
  - OpenAPI documentation at `/docs`

## 📋 Tech Stack

- **Python 3.12** (latest stable)
- **FastAPI** - Async web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Docker & Docker Compose** - Containerization
- **pytest + httpx** - Testing

## 🏗️ Architecture

Clean architecture with separation of concerns:
- **Routers** - Thin HTTP layer, validation
- **Services** - Business logic, transactions
- **Repositories** - Database operations only
- **Models** - SQLAlchemy ORM models
- **Schemas** - Pydantic request/response models

## 🚦 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.12+ and PostgreSQL 16

### Option 1: Docker Compose (Recommended)

1. Clone and navigate to the project:
```bash
git clone <repo-url>
cd Whatsapp-backend
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker-compose up -d
```

This will start:
- **API** at http://localhost:8000
- **PostgreSQL** at localhost:5432
- **pgAdmin** at http://localhost:5050 (admin@clinic.local / admin)

4. Access the API:
- OpenAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Option 2: Local Development

1. Create and activate virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Set up PostgreSQL and update `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/appointment_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/appointment_db
```

4. Run migrations:
```powershell
alembic upgrade head
```

5. Start the API:
```powershell
uvicorn app.main:app --reload
```

## 🧪 Running Tests

### Integration Tests (with Docker)

1. Start test database:
```powershell
docker-compose up -d postgres
```

2. Create test database:
```powershell
docker exec -it clinic_postgres psql -U postgres -c "CREATE DATABASE clinic_test_db;"
```

3. Run tests:
```powershell
pytest tests/integration/ -v
```

### Key Tests Include:
- ✅ **Normal booking flow** - 10 appointments succeed, 11th fails
- ✅ **Concurrency test** - 30 concurrent bookings, exactly 10 succeed
- ✅ **Idempotency** - Same key returns same appointment
- ✅ **Check-in flow** - Queue positions assigned in order
- ✅ **Date validation** - Check-in only on appointment date

### Run Concurrency Test Only:
```powershell
pytest tests/integration/test_appointments.py::TestConcurrentBooking -v
```

## 📝 Database Migrations

Create a new migration:
```powershell
alembic revision --autogenerate -m "description"
```

Apply migrations:
```powershell
alembic upgrade head
```

Rollback one migration:
```powershell
alembic downgrade -1
```

## 🔌 API Examples

### 1. Create Patient
```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 34,
    "phone": "+919876543210",
    "email": "john@example.com"
  }'
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "last_name": "Doe",
  "age": 34,
  "phone": "+919876543210",
  "email": "john@example.com",
  "created_at": "2025-11-12T10:30:00Z"
}
```

### 2. Create Doctor
```bash
curl -X POST http://localhost:8000/api/v1/doctors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Smith",
    "code": "DR_SMITH_001",
    "specialty": "Cardiology"
  }'
```

### 3. Set Doctor Availability
```bash
curl -X POST http://localhost:8000/api/v1/doctors/{doctor_id}/availability \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-15",
    "is_present": true,
    "notes": "Morning shift"
  }'
```

### 4. Book Appointment (Idempotent)
```bash
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "{patient_id}",
    "doctor_id": "{doctor_id}",
    "date": "2025-11-15",
    "idempotency_key": "booking-abc-123"
  }'
```

**Response:**
```json
{
  "id": "appointment-uuid",
  "patient_id": "patient-uuid",
  "doctor_id": "doctor-uuid",
  "date": "2025-11-15",
  "slot": 1,
  "status": "booked",
  "created_at": "2025-11-12T10:35:00Z",
  "updated_at": "2025-11-12T10:35:00Z"
}
```

**Note**: Repeating the same request with the same `idempotency_key` returns the same appointment without consuming another slot.

### 5. Check In (On Appointment Date Only)
```bash
curl -X POST http://localhost:8000/api/v1/checkins \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_id": "{appointment_id}",
    "patient_id": "{patient_id}"
  }'
```

**Response:**
```json
{
  "queue_position": 1,
  "checked_in_at": "2025-11-15T09:00:00Z",
  "appointment_id": "appointment-uuid"
}
```

### 6. Get Doctor's Queue
```bash
curl -X GET "http://localhost:8000/api/v1/checkins/doctors/{doctor_id}/queue?date=2025-11-15"
```

### 7. List Doctor's Appointments
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/doctors/{doctor_id}/appointments?date=2025-11-15"
```

## 🔐 Business Rules

1. **Capacity Enforcement**: Max 10 appointments per doctor per day
   - Enforced atomically via database UPDATE with RETURNING
   - Concurrent bookings are handled safely
   
2. **Idempotency**: Global idempotency_key prevents duplicate bookings
   - Same key always returns the same appointment
   - Does not consume additional slots

3. **Doctor Availability**: 
   - If `DoctorDailyAvailability` exists with `is_present=false`, booking fails (422)
   - If no availability record exists, booking is allowed (default available)

4. **Check-in Rules**:
   - Only allowed on the appointment date (server timezone)
   - Queue positions assigned atomically in check-in order
   - Duplicate check-in returns 409 Conflict

5. **Database Constraints**:
   - Unique `(doctor_id, date, slot)` prevents slot conflicts
   - Unique `(doctor_id, date, position)` prevents queue position conflicts

## 📊 Database Schema

### Key Tables:
- **patients** - Patient records with normalized phone
- **doctor_masters** - Doctor information
- **doctor_daily_availabilities** - Doctor availability per date
- **doctor_daily_capacities** - Remaining slots per doctor per day
- **appointments** - Booking records with idempotency support
- **queue_entries** - Check-in queue with positions

All tables use UUID primary keys and timestamptz for timestamps.

## 🔧 Configuration

Key environment variables (see `.env.example`):

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DATABASE_URL_SYNC=postgresql://user:pass@host:5432/db
LOG_LEVEL=INFO
ENVIRONMENT=development
MAX_APPOINTMENTS_PER_DOCTOR_PER_DAY=10
```

## 📈 Monitoring & Logging

- **Structured JSON logs** with log level, message, and context
- **PHI redaction** for phone, email, names in logs
- **Health check endpoint**: `GET /health`
- **OpenAPI docs**: `GET /docs` and `GET /redoc`

## 🐛 Error Handling

Consistent error responses:
```json
{
  "error": "ErrorCode",
  "message": "Human-readable message",
  "details": {}
}
```

HTTP Status Codes:
- `201` - Resource created
- `200` - Success
- `400` - Validation error
- `404` - Resource not found
- `409` - Conflict (capacity full, duplicate check-in)
- `422` - Business rule violation (doctor unavailable)
- `500` - Internal server error

## 🧹 Code Quality

Run linting:
```powershell
ruff check .
black --check .
```

Format code:
```powershell
black .
```

## 🤝 Contributing

1. Follow SOLID principles
2. Keep routers thin - business logic in services
3. Write tests for new features
4. Use type hints and docstrings
5. Run tests before committing

## 📄 License

MIT License - see LICENSE file

## 🆘 Support

For issues or questions:
1. Check OpenAPI docs at `/docs`
2. Review integration tests for usage examples
3. Check logs for error details

---

**Built with ❤️ using FastAPI, SQLAlchemy, and PostgreSQL**
