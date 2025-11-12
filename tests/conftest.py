import pytest
import pytest_asyncio
from datetime import date, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.models import Base
from app.db.session import get_db
from app.core.config import get_settings

settings = get_settings()

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinic_test_db"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a new database session and engine for each test"""
    # Create a fresh engine for this test
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=30,
    )
    
    # Setup: create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session maker
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Return the session maker so each request gets its own session
    yield async_session
    
    # Cleanup: dispose engine after test
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Async HTTP client for testing with overridden database
    
    Each request will get its own database session from the session maker.
    """
    async def override_get_db():
        async with db_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_patient(client, db_session):
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


@pytest_asyncio.fixture
async def test_doctor(client, db_session):
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


@pytest_asyncio.fixture
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
