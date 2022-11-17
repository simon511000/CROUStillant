from Crous.requests import get_crous_menu, get_crous_info

from utils.data import restos
from utils.embeds import load_embed
from utils.views import Menu


import discord
from discord import app_commands
from discord.ext import commands


import typing
import pytz


from datetime import datetime, timedelta



# All the restaurants, need to be added later...
"""
        restaurant: typing.Literal[
            "CHALONS - ENSAM - Resto U ENSAM",
            "CHARLEVILLE - Centre - Resto U Maison des étudiants",
            "CHARLEVILLE - P.H.T. - Resto U Moulin Le Blanc",
            "REIMS - Campus Lettres - Resto U Jean-Charles Prost",
            "REIMS - Campus Lettres - Resto U Paul Fort",
            "REIMS - Campus Lettres - Resto U Pôle santé",
            "REIMS - Campus Lettres - Resto U SciencesPo",
            "REIMS - Campus Sciences - Resto U Moulin de la Housse",
            "REIMS - Campus Sciences - Resto U INSPE de REIMS",
            "REIMS - Campus Sciences - Cafet IUT Reims",
            "REIMS - Campus Sciences - Cafet Evariste Galois",
            "REIMS - Campus Sciences - Cafet Sciences",
            "TROYES - Campus - Resto U Les Lombards",
            "TROYES - Campus - Cafet IUT Troyes",
            "TROYES - Campus - Brasserie UTT",
            "TROYES - Centre - Resto U Les Courtines"
        ], 
"""

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
        restaurant: typing.Literal[
            "REIMS - Campus Sciences - Resto U Moulin de la Housse",
            "TROYES - Campus - Resto U Les Lombards",
        ], 
        salon : discord.TextChannel,
    ):
        await interaction.response.defer(ephemeral=True)
        

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
                    self.client.session, 
                    restos[restaurant], 
                    new_date.strftime("%Y-%m-%d")
                )

                infos = get_crous_info(
                    restos[restaurant]
                )
                run= False
                count += 1

                if count >= 7:
                    run = False 
                    return await interaction.followup.send(content="Une erreur inatendue est survenu...", ephemeral=True) 
            except Exception as e:
                self.client.log(e)
                pass
        
        
        data = await load_embed(self.client, restos[restaurant], infos, menus.dates, paris_dt)
        view = Menu(infos, data[0], data[1], data[2])
        
        try:
            msg = await salon.send(embed=data[0][0], view=view)

            async with interaction.client.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM settings WHERE id = $1", interaction.guild.id)
            data = [dict(row) for row in rows]

            if data == []:
                async with self.client.pool.acquire() as conn:
                    await conn.execute("INSERT INTO settings (id, rid, channel, message, timestamp) VALUES ($1, $2, $3, $4, $5)", interaction.guild.id, restos[restaurant], salon.id, msg.id, datetime.utcnow().timestamp())
            else:
                async with interaction.client.pool.acquire() as conn:
                    await conn.execute("UPDATE settings SET rid = $1, channel = $2, message = $3, timestamp = $4 WHERE id = $5", restos[restaurant], salon.id, msg.id, datetime.utcnow().timestamp(), interaction.guild.id)

            return await interaction.followup.send(content=f"Le Menu est configurer dans {salon.mention}, il se mettra à jour chaue jour a minuit.", ephemeral=True)
        except discord.errors.Forbidden:
            return await interaction.followup.send(content=f"Je n'ai pas la permission d'envoyé des messages dans {salon.mention}", ephemeral=True)
        except:
            return await interaction.followup.send(content="Une erreur inatendue est survenu...", ephemeral=True) 


      
    @commands.command(help="sync", hidden=True)
    @commands.is_owner()
    async def sync(self, ctx):
        await self.client.tree.sync(guild=discord.Object(id=802797875457294347))
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