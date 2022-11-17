from utils.task import run_task


from discord.ext import commands, tasks


import pytz


from datetime import time


time_to_execute = time(hour=1, minute=0, tzinfo=pytz.timezone("Europe/Paris"))


class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.daily_task.start()


    def cog_unload(self):
        self.daily_task.cancel()


    def cog_reload(self):
        self.daily_task.cancel()


    @tasks.loop(time=time_to_execute)
    async def daily_task(self):
        await run_task(self.client)


async def setup(client):
    await client.add_cog(Tasks(client))