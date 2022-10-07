from Crous.requests import get_crous_menu

from utils.image import image


import discord


import datetime
import pytz


async def load_embed(client, rid, infos, dates, paris_dt):
    embeds = []
    options = []

    
    # Week-ends
    if int(paris_dt.strftime("%w")) == 5 or int(paris_dt.strftime("%w")) == 6 or int(paris_dt.strftime("%w")) == 0:
        dates.pop(0) # remove Friday


    index = 0
    for date in dates:
        year = paris_dt.strftime('%Y')

        month = str(date.split('-')[1])
        day = str(date.split('-')[0])

        try:
            menu = await get_crous_menu(
                client.session, 
                rid, 
                f"{year}-{month}-{day}"
            )

            if month.startswith('0'):
                month = month[1:]
            if day.startswith('0'):
                day = day[1:]


            clean_date = pytz.timezone("Europe/Paris").localize(datetime.datetime(int(year), int(month), int(day)), is_dst=None).strftime('%A %d %B')


            embed = discord.Embed(title=f"{infos.nom}", description=f"**`•` Menu du `{date.replace('-', '/')}/{year}`**\n**`•` Updated**: <t:{int(datetime.datetime.utcnow().timestamp())}:R> (<t:{int(datetime.datetime.utcnow().timestamp())}>)\n\u2063", color=client.color, url=infos.url)
            embed.add_field(name="__Traditionnel__\n\u2063", value=f"**Entrées**:\n- {menu.tradi.entrees_format}\n\n**Plats**:\n- {menu.tradi.plats_format}\n\n**Desserts**:\n- {menu.tradi.deserts_format}")
            embed.add_field(name="ㅤㅤ", value="ㅤㅤ")
            embed.add_field(name="__Brasserie__\n\u2063", value=f"**Entrées**:\n- {menu.brasserie.entrees_format}\n\n**Plats**:\n- {menu.brasserie.plats_format}\n\n**Desserts**:\n- {menu.brasserie.deserts_format}")
            embed.set_thumbnail(url=client.avatar_url)
            embed.set_footer(text=client.footer_text, icon_url=client.avatar_url)
        except:
            embed = discord.Embed(title=f"Error 404", description=f"**`•` Le CROUS ne fournit pas d'information actuellement pour ce restaurant...**", color=client.color, url=infos.url)
        
    
        if index == 0:
            options.append(discord.SelectOption(label=clean_date, description=f"{infos.nom} - {date.replace('-', '/')}", value=index, default=True))
        else:
            options.append(discord.SelectOption(label=clean_date, description=f"{infos.nom} - {date.replace('-', '/')}", value=index, default=False))
        
        embeds.append(embed)

        index += 1


    ru_map = await image(
        url=f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/static/geojson(%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{infos.coords[0]}1%2C{infos.coords[1]}%5D%7D)/{infos.coords[0]},{infos.coords[1]},15.25,0,0/1000x400?access_token={client.mapbox}",
        title="map",
        session=client.session
    )

    return (embeds, options, ru_map)