import pytest
import asyncio
from datetime import date, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.models import Base
from app.db.session import get_db
from app.core.config import get_settings

settings = get_settings()

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinic_test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database tables before tests and drop after"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    """Async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_patient(client):
    """Create a test patient"""
    response = await client.post(
        "/api/v1/patients",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "phone": "+919876543210",
            "email": "john@example.com"
        }
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_doctor(client):
    """Create a test doctor"""
    response = await client.post(
        "/api/v1/doctors",
        json={
            "name": "Dr. Smith",
            "code": "DR_SMITH_001",
            "specialty": "General Medicine"
        }
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def test_doctor_with_availability(client, test_doctor):
    """Create doctor with availability for today"""
    today = date.today()
    response = await client.post(
        f"/api/v1/doctors/{test_doctor['id']}/availability",
        json={
            "date": today.isoformat(),
            "is_present": True,
            "notes": "Available today"
        }
    )
    assert response.status_code == 200
    return test_doctor


@pytest.fixture
async def clean_db():
    """Clean database between tests"""
    async with test_engine.begin() as conn:
        await conn.execute("TRUNCATE TABLE queue_entries, appointments, doctor_daily_capacities, doctor_daily_availabilities, doctor_masters, patients RESTART IDENTITY CASCADE")
    yield
