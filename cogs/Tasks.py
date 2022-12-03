from utils.task import run_task


from discord.ext import commands, tasks


import pytz


from datetime import time


class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.first_task.start()
        self.second_task.start()


    def cog_unload(self):
        self.first_task.cancel()
        self.second_task.cancel()


    def cog_reload(self):
        self.first_task.cancel()
        self.second_task.cancel()


    @tasks.loop(time=time(hour=1, minute=0, tzinfo=pytz.timezone("Europe/Paris")))
    async def first_task(self):
        await run_task(self.client)

    
    @tasks.loop(time=time(hour=9, minute=0, tzinfo=pytz.timezone("Europe/Paris")))
    async def second_task(self):
        await run_task(self.client)


async def setup(client):
    await client.add_cog(Tasks(client))