import aiohttp
from utils import Log

__all__ = ["get"]


async def get(url, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=kwargs) as response:
            if response.status != 200:
                Log.error("API", f"Failed to fetch data: {response.status}")
                return None
            return await response.json()
