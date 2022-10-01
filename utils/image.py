import discord

import aiohttp

from io import BytesIO


async def image(url, title:str="image", session = aiohttp.ClientSession()):
    async with session.get(url) as resp:
        image_binary = BytesIO(await resp.read())
        image_binary.seek(0)
        return discord.File(fp=image_binary, filename=f'{title}.png')