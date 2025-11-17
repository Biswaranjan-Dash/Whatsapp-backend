import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        resp = await client.post('/api/v1/patients', json={
            'name': 'Test Patient',
            'age': 30,
            'gender': 'male',
            'phone': '+919876543210'
        })
        print(f'Status: {resp.status_code}')
        print(f'Response: {resp.text}')

asyncio.run(test())
