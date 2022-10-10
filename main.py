from utils.task import run_task


import discord
from discord.ext import commands


import logging
import asyncpg
import asyncio


from asyncpg.exceptions import UndefinedTableError
from os import listdir, environ
from pathlib import Path
from time import time
from datetime import datetime
from dotenv import load_dotenv
from aiohttp import ClientSession
from datetime import datetime, timedelta


load_dotenv(dotenv_path=f"{str(Path(__file__).parents[0])}/.env")


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents(
            messages = True, # for syncing purposes
            guilds = True # to get guild channels information
        )
        super().__init__(
            command_prefix = commands.when_mentioned_or("&"), 
            intents=intents, 
            owner_ids = [
                647487369246801921, # Polsulpicien#5020
            ], 
            help_command = None,
            allowed_mentions = discord.AllowedMentions( # Better to prevent any issues
                everyone=False, 
                users=True, 
                roles=False, 
                replied_user=True
            ),
            slash_commands = True,
            activity = discord.Activity(name=f"Crous Restaurants", type=discord.ActivityType.watching),
            status = discord.Status.online
        )


        # Embed Color
        self.color = 0x2F3136

        # API KEY
        self.mapbox = environ['mapbox']
            
        # Bot Path
        self.path = str(Path(__file__).parents[0])
        

        self.footer_text = f"CrousBot • v1.0.1 - Crée par Polsu Development" 


        # Variables
        self.logs = None
        self.ready = False
        self.cache = {}

        self.launch = str(time()).split(".")[0]
        self.launch_time = datetime.utcnow()

    
        # Logging
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        
        self.log = logging.getLogger()
        self.log.setLevel(logging.INFO)
        
        handler = logging.FileHandler(f"{self.path}/logging/logs.log") # Error Handler
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(handler)
        
        handler = logging.FileHandler(f"{self.path}/logging/info.log") # Info handler
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(handler)
        
    
        self.log.info("New Boot\n---------------------------------------------------------")
    
    
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)

        self.log.info('Logged in as')
        self.log.info(self.user.name)
        self.log.info(self.user.id)
        
        print(f"CrousBot is now on!\n>> {datetime.utcnow()}\n")
        self.log.info(f"CrousBot is now on!\n>> {datetime.utcnow()}\n")
        self.ready = True

        self.avatar_url = self.user.avatar.url

        await run_task(self)


    async def close(self):
        await self.session.close()
        await self.pool.close()
        await super().close()


    async def run(self):
        # > DataBase

        # Create Pool, connection to dB:
        self.pool = await asyncpg.create_pool(database="Crous", user="postgres", password=environ['postgres'], host="127.0.0.1")


        # Create a new table if necessary:

        # Settings:
        # - id INT (guild ID)
        # - channel (channel ID)
        # - message (message ID)
        # - rid (restaurant ID)
        # - timestamp (UTC timestamp, when the server was added to the dB)
        
        # This table will store all the IDs for the task...

        try:
            async with self.pool.acquire() as conn:
                await conn.fetch('SELECT * FROM settings')
        except UndefinedTableError:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    CREATE TABLE settings (
                        id BIGINT PRIMARY KEY, 
                        channel BIGINT,
                        message BIGINT,
                        rid VARCHAR(4),
                        timestamp BIGINT
                    );
                """)



        for file in listdir(self.path + "/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    self.log.info(f"Loaded {file[:-3]} cog")
                except Exception as e:
                    self.log.error(f"Error loading {file[:-3]} cog: {e}")


async def main():
    client = Bot()

    async with ClientSession() as session:
        async with client:
            client.session = session
            client.ssl = False
            await client.run()
            await client.start(environ["token"], reconnect=True)


asyncio.run(main())