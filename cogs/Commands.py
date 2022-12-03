from Crous.requests import get_menu

from utils.embeds import load_embed
from utils.views import Menu


import discord
from discord import app_commands
from discord.ext import commands


import json

from datetime import datetime
from pathlib import Path
from io import BytesIO


path = str(Path(__file__).parents[0].parents[0])


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @app_commands.command(name="crous", description="Configurez le CrousBot sur votre serveur.")
    @app_commands.describe(restaurant="Choisissez votre Restaurant Crous.")
    @app_commands.describe(salon="Choisissez dans quel salon le repas sera affiché.")
    @app_commands.default_permissions(manage_guild=True)
    async def crous(
        self, 
        interaction: discord.Interaction,
        restaurant: str, 
        salon : discord.TextChannel,
    ):
        await interaction.response.defer(ephemeral=True)


        with open(f"{path}/data.json", "r") as f:
            config = json.load(f)

        try:
            if str(restaurant).startswith("r"):
                config[restaurant]['nom']
                rid = restaurant
            else:
                raise AttributeError
        except:
            return await interaction.followup.send(content="Ce restaurant n'existe pas!", ephemeral=True)

        d = await get_menu(interaction.client.session, rid)
        
        data = await load_embed(interaction.client, d)
        view = Menu(d.info, data[0], data[1])

        with BytesIO() as image_binary:
            data[3].save(image_binary, 'PNG')
            image_binary.seek(0)
            ru_map = discord.File(fp=image_binary, filename=f'map.png')

        try:
            msg = await salon.send(embeds=[data[2], data[0][0]], file=ru_map, view=view)

            async with interaction.client.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM settings WHERE id = $1", interaction.guild.id)
            data = [dict(row) for row in rows]

            if data == []:
                async with self.client.pool.acquire() as conn:
                    await conn.execute("INSERT INTO settings (id, rid, channel, message, timestamp) VALUES ($1, $2, $3, $4, $5)", interaction.guild.id, rid, salon.id, msg.id, datetime.utcnow().timestamp())
            else:
                async with interaction.client.pool.acquire() as conn:
                    await conn.execute("UPDATE settings SET rid = $1, channel = $2, message = $3, timestamp = $4 WHERE id = $5", rid, salon.id, msg.id, datetime.utcnow().timestamp(), interaction.guild.id)

            return await interaction.followup.send(content=f"Le Menu est configurer dans {salon.mention}, il se mettra à jour chaque jour entre miniut et 3 heures!", ephemeral=True)
        except discord.errors.Forbidden:
            return await interaction.followup.send(content=f"Je n'ai pas la permission d'envoyé des messages dans {salon.mention}", ephemeral=True)
        except:
            return await interaction.followup.send(content="Une erreur inatendue est survenu...", ephemeral=True) 


    @crous.autocomplete('restaurant')
    async def crous_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ):
        with open(f"{path}/data.json", "r") as f:
            config = json.load(f)

        count = 0 
        result = []
        for x in config:
            if str(x).startswith("r") and current.lower() in str(config[x]['nom']).lower():
                result.append(app_commands.Choice(name=f"{config[x]['zone']} - {config[x]['nom']}", value=x))
                count += 1

            if count == 25:
                break

        return result



    @commands.command(help="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        await self.client.tree.sync()
        await ctx.send("Done")



    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        try:
            async with self.client.pool.acquire() as conn:
                await conn.execute("DELETE FROM Settings WHERE id = $1", guild.id)
        except:
            pass

                       
async def setup(client):
    await client.add_cog(Commands(client))