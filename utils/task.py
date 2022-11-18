from Crous.requests import get_crous_info, load_dates

from utils.embeds import load_embed
from utils.views import Menu


import discord


import pytz

from datetime import timedelta, datetime


async def run_task(client):
    async with client.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM settings")
    guilds = [dict(row) for row in rows]

    for guild in guilds:
        rid = guild.get('rid')

        if rid not in client.cache:
            paris_dt = pytz.timezone("Europe/Paris").localize(datetime.now(), is_dst=None)

            # Week-ends
            if int(paris_dt.strftime("%w")) == 5:
                new_date =paris_dt + timedelta(hours=72)
            elif int(paris_dt.strftime("%w")) == 6:
                new_date = paris_dt + timedelta(hours=48)
            else:
                new_date = paris_dt + timedelta(hours=24)


            dates = load_dates(
                client.session,
                rid, 
                new_date.strftime("%Y-%m-%d")
            )
            
            infos = get_crous_info(
                rid
            )
            
            data = await load_embed(client, rid, infos, dates, paris_dt)
            view = Menu(infos, data[0], data[1], data[2])

            client.cache[rid] = (data, view)
        else:
            data = client.cache[rid][0]
            view = client.cache[rid][1]
        

        try:
            channel = client.get_channel(guild.get('channel'))

            if guild.get('message') == None:
                message = await channel.send(embed=data[0][0], view=view)

                async with client.pool.acquire() as conn:
                    await conn.execute("UPDATE settings SET message = $1 WHERE id = $2", message.id, guild.get('id'))
            else:
                try:
                    message = await channel.fetch_message(guild.get('message'))
                    await message.edit(embed=data[0][0], view=view)
                except:
                    # If the message was deleted, the bot tries to send the message again...
                    try:
                        message = await channel.send(embed=data[0][0], view=view)

                        async with client.pool.acquire() as conn:
                            await conn.execute("UPDATE settings SET message = $1 WHERE id = $2", message.id, guild.get('id'))
                    except discord.errors.HTTPException:
                        # Discord Server Errors 
                        pass
                    except AttributeError:
                        async with client.pool.acquire() as conn:
                            await conn.execute("DELETE FROM settings WHERE id = $1", guild.get('id'))            
        except discord.errors.HTTPException:
            # Discord Server Errors 
            pass
        except AttributeError:
            async with client.pool.acquire() as conn:
                await conn.execute("DELETE FROM settings WHERE id = $1", guild.get('id'))

    client.cache = {}