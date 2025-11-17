"""Reset database schema - drops all tables and recreates them"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinic_db"
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/clinic_test_db"

async def reset_database():
    """Drop all tables and recreate them"""
    print("Connecting to database...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    print("\nDropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("\nCreating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("\n✅ Database reset complete!")

async def reset_test_database():
    """Drop all tables and recreate them in test database"""
    print("\nConnecting to test database...")
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    print("\nDropping all test tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("\nCreating all test tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("\n✅ Test database reset complete!")

if __name__ == "__main__":
    print("=" * 60)
    print("RESETTING DATABASES")
    print("=" * 60)
    asyncio.run(reset_database())
    asyncio.run(reset_test_database())
    print("\n" + "=" * 60)
    print("ALL DONE!")
    print("=" * 60)
