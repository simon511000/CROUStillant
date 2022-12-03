from Crous.requests import get_menu

from utils.embeds import load_embed
from utils.views import Menu


import discord


from io import BytesIO


async def run_task(client):
    async with client.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM settings")
    guilds = [dict(row) for row in rows]

    for guild in guilds:
        rid = guild.get('rid')

        if rid not in client.cache:
            d = await get_menu(client.session, rid)
            
            data = await load_embed(client, d)
            view = Menu(d.info, data[0], data[1])

            client.cache[rid] = (data, view)
        else:
            data = client.cache[rid][0]
            view = client.cache[rid][1]

        with BytesIO() as image_binary:
            data[3].save(image_binary, 'PNG')
            image_binary.seek(0)
            ru_map = discord.File(fp=image_binary, filename=f'mojang_ping.png')

        try:
            channel: discord.TextChannel = client.get_channel(guild.get('channel'))

            if guild.get('message') == None:
                message = await channel.send(embeds=[data[2], data[0][0]], file=ru_map, view=view)

                async with client.pool.acquire() as conn:
                    await conn.execute("UPDATE settings SET message = $1 WHERE id = $2", message.id, guild.get('id'))
            else:
                try:
                    message = await channel.fetch_message(guild.get('message'))
                    await message.edit(embeds=[data[2], data[0][0]], attachments=[ru_map], view=view)
                except:
                    # If the message was deleted, the bot tries to send the message again...
                    try:
                        message = await channel.send(embeds=[data[2], data[0][0]], file=ru_map, view=view)

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