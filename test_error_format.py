import asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test 404
        resp = await client.get(f"/api/v1/patients/{uuid.uuid4()}")
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.json()}")
        print(f"Keys: {list(resp.json().keys())}")

asyncio.run(test())
