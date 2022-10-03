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
    async def wait_until_time(self):
        now = datetime.now(pytz.timezone("Europe/Paris"))

        task = self.daily_task
        interval = timedelta(hours=task.hours, minutes=task.minutes, seconds=task.seconds)

        next_run = now.replace(hour=24, minute=0, second=0)

        while next_run > now:
            next_run -= interval
        next_run += interval

        await discord.utils.sleep_until(next_run)



async def setup(client):
    await client.add_cog(Tasks(client))