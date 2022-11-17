from Crous.requests import get_crous_menu

from utils.image import image


import discord


import datetime


def get_clean_date(day, raw_day, month, paris_dt):
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembtre", "Octobre", "Novembre", "Décembre"]

    if int(paris_dt.strftime("%d")) + 1 == day:
        return f"Demain - {jours[day]} {raw_day} {mois[month]}"
    else:
        return f"{jours[day]} {raw_day} {mois[month]}"


async def load_embed(client, rid, infos, dates, paris_dt):
    embeds = []
    options = []

    
    # Week-ends
    if int(paris_dt.strftime("%w")) == 5 or int(paris_dt.strftime("%w")) == 6 or int(paris_dt.strftime("%w")) == 0:
        dates.pop(0) # remove Friday


    # Sometimes, yesterday's Menu is still available, so we remove it
    if (paris_dt - datetime.timedelta(days=1)).strftime("%d-%m") == dates[0]:
        dates.pop(0)


    index = 0
    for date in dates:
        if not "-" in date:
            continue

        try:
            year = paris_dt.strftime('%Y')

            month = str(date.split('-')[1])
            day = str(date.split('-')[0])


            clean_date = get_clean_date(int(paris_dt.strftime('%w'))-1, int(paris_dt.strftime('%m'))-1, day, paris_dt)

            menu = await get_crous_menu(
                client.session, 
                rid, 
                f"{year}-{month}-{day}"
            )

            if month.startswith('0'):
                month = month[1:]
            if day.startswith('0'):
                day = day[1:]

            embed = discord.Embed(title=f"{infos.nom}", description=f"**`•` Menu du `{date.replace('-', '/')}/{year}`**\n**`•` Mis à jour**: <t:{int(datetime.datetime.utcnow().timestamp())}:R> (<t:{int(datetime.datetime.utcnow().timestamp())}>)\n\u2063", color=client.color, url=infos.url)
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