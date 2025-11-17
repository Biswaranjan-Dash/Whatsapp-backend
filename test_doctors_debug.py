"""Debug script to test doctors endpoint"""
import asyncio
import httpx


async def test_doctors():
    # Use 127.0.0.1 instead of localhost to avoid Windows IPv6/IPv4 issues
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        try:
            response = await client.get("/api/v1/doctors")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                print(f"JSON: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_doctors())
