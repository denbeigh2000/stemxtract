import asyncio

from discord.http import HTTPClient
from discord.types.user import User


async def discord_identity(token: str) -> str:
    client = HTTPClient(loop=asyncio.get_running_loop())
    user: User = await client.static_login(token)

    return str(user["id"])
