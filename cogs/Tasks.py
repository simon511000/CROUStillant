import discord
from discord.ext import commands, tasks


import pytz


from datetime import datetime, timedelta


class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.daily_task.start()
        

    def cog_unload(self):
        self.daily_task.cancel()
        
    def cog_reload(self):
        self.daily_task.cancel()



    @tasks.loop(hours=24)
    async def daily_task(self):
        await self.client.run_task()



    @daily_task.before_loop
    async def wait_until_7am(self):
        print("Waiting for the bot to be ready...")
        await self.client.wait_until_ready()

        paris_dt = pytz.timezone("Europe/Paris").localize(datetime.now(), is_dst=None)
        next_run = paris_dt.replace(hour=24, minute=0, second=0)

        if next_run < paris_dt:
            next_run += timedelta(days=1)

        await discord.utils.sleep_until(next_run)


async def setup(client):
    await client.add_cog(Tasks(client))