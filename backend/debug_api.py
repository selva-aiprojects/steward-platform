import httpx
import asyncio
import traceback

async def debug_api():
    print("Testing API @ http://127.0.0.1:8000")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://127.0.0.1:8000/health", timeout=10.0)
            print(f"Health Status: {r.status_code}")
            print(f"Health Body: {r.json()}")
        except Exception as e:
            print(f"Health Check Failed: {e}")
            traceback.print_exc()

        try:
            r = await client.get("http://127.0.0.1:8000/api/v1/users/1")
            print(f"User #1 Status: {r.status_code}")
            print(f"User #1 Body: {r.json() if r.status_code == 200 else r.text}")
        except Exception as e:
            print(f"User Retrieval Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_api())
