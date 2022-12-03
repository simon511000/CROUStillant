import discord

import aiohttp

from io import BytesIO
from PIL import Image


async def image(url, session = aiohttp.ClientSession()):
    async with session.get(url) as resp:
        im = Image.open(BytesIO(await resp.read()))

        with BytesIO() as image_binary:
            im.save(image_binary, 'PNG')
            image_binary.seek(0)
            return im