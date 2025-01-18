import aiohttp
from utils import Log

__all__ = ["get"]


async def get(
    url: str,
    headers: dict = None,
    name_message: str = None,
    error_message: str = None,
    **params,
):
    Log.info("API", f"{url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers or {}) as response:
            if not response.ok:
                Log.error(
                    name_message or "API",
                    (
                        error_message.format(
                            response=response, text=await response.text()
                        )
                        if error_message
                        else f"Failed to fetch data: {response.status}"
                    ),
                )
                return None
            return await response.json()
