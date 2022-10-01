
from Crous.requests import get_crous_menu, get_crous_info

from utils.embeds import load_embed
from utils.views import Menu


import discord
from discord.ext import commands


import logging
import asyncpg
import json
import asyncio
import pytz


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
            status = discord.Status.idle
        )


        # Embed Color
        self.color = 0x2F3136

        # API KEY
        self.mapbox = environ['mapbox']
            
        # Bot Path
        self.path = str(Path(__file__).parents[0])
        

        self.footer_text = f"CrousBot • v1.0.1 - Made by Polsu Development" 


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
        
        await self.run_task()


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



    async def run_task(self):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM settings")
        guilds = [dict(row) for row in rows]

        for guild in guilds:
            rid = guild.get('rid')

            if rid not in self.cache:
                paris_dt = pytz.timezone("Europe/Paris").localize(datetime.now(), is_dst=None)

                # Week-ends
                if int(paris_dt.strftime("%w")) == 5:
                    new_date =paris_dt + timedelta(hours=72)
                elif int(paris_dt.strftime("%w")) == 6:
                    new_date = paris_dt + timedelta(hours=48)
                else:
                    new_date = paris_dt + timedelta(hours=24)


                # If there is no menu for a date it tries the next 7 days or fails.
                # Could be improve, and will be improved, but lazy for now :D

                run = True
                count = 0
                while run:
                    try:
                        menus = await get_crous_menu(
                            self.session, 
                            rid, 
                            new_date.strftime("%Y-%m-%d")
                        )

                        infos = get_crous_info(
                            rid
                        )
                        run= False
                        count += 1

                        if count >= 7:
                            run = False 
                            break
                    except:
                        pass
                
                data = await load_embed(self, rid, infos, menus.dates, paris_dt)
                view = Menu(infos, data[0], data[1], data[2])

                self.cache[rid] = (data, view)
            else:
                data = self.cache[rid][0]
                view = self.cache[rid][1]
            
            

            try:
                channel = self.get_channel(guild.get('channel'))

                if guild.get('message') == None:
                    message = await channel.send(embed=data[0][0], view=view)

                    async with self.pool.acquire() as conn:
                        await conn.execute("UPDATE settings SET message = $1 WHERE id = $2", message.id, guild.get('id'))
                else:
                    try:
                        message = await channel.fetch_message(guild.get('message'))
                        await message.edit(embed=data[0][0], view=view)
                    except:
                        # If the message was deleted, the bot tries to send the message again...
                        try:
                            message = await channel.send(embed=data[0][0], view=view)

                            async with self.pool.acquire() as conn:
                                await conn.execute("UPDATE settings SET message = $1 WHERE id = $2", message.id, guild.get('id'))
                        except discord.errors.HTTPException:
                            # Discord Server Errors 
                            pass
                        except AttributeError:
                            async with self.pool.acquire() as conn:
                                await conn.execute("DELETE FROM settings WHERE id = $1", guild.get('id'))            
            except discord.errors.HTTPException:
                # Discord Server Errors 
                pass
            except AttributeError:
                async with self.pool.acquire() as conn:
                    await conn.execute("DELETE FROM settings WHERE id = $1", guild.get('id'))



async def main():
    client = Bot()

    async with ClientSession() as session:
        async with client:
            client.session = session
            client.ssl = False
            await client.run()
            await client.start(environ["token"], reconnect=True)


asyncio.run(main())
