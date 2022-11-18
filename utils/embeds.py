from Crous.requests import get_crous_menu

from utils.image import image


import discord


import datetime
import pytz


def get_clean_date(day, month, year):
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembtre", "Octobre", "Novembre", "Décembre"]

    date = pytz.timezone("Europe/Paris").localize(datetime.datetime(int(year), int(month), int(day)), is_dst=None)

    return f"{jours[int(date.strftime('%w'))-1]} {day} {mois[int(date.strftime('%m'))-1]}"


async def load_embed(client, rid, infos, dates, paris_dt):
    embeds = []
    options = []

    
    # Week-ends
    if int(paris_dt.strftime("%w")) == 6 or int(paris_dt.strftime("%w")) == 0:
        dates.pop(0) # remove Friday


    # Sometimes, yesterday's Menu is still available, so we remove it
    if (paris_dt - datetime.timedelta(days=1)).strftime("%d-%m") == dates[0]:
        dates.pop(0)


    index = 0
    for date in dates:
        try:
            year = paris_dt.strftime('%Y')

            month = str(date.split('-')[1])
            day = str(date.split('-')[0])

            clean_date = get_clean_date(int(day), int(month), int(year))


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
            embed.add_field(name=f"{menu.part1.title}\n\u2063", value=f"**{menu.part1.f1}**:\n- {menu.part1.val1}\n\n**{menu.part1.f2}**:\n- {menu.part1.val2}\n\n**{menu.part1.f3}**:\n- {menu.part1.val3}")
            embed.add_field(name="ㅤㅤ", value="ㅤㅤ")
            if menu.part2.val3 == "":
                embed.add_field(name=f"{menu.part2.title}\n\u2063", value=f"**{menu.part2.f1}**:\n- {menu.part2.val1}\n\n**{menu.part2.f2}**:\n- {menu.part2.val2}")
            else:
                embed.add_field(name=f"{menu.part2.title}\n\u2063", value=f"**{menu.part2.f1}**:\n- {menu.part2.val1}\n\n**{menu.part2.f2}**:\n- {menu.part2.val2}\n\n**{menu.part2.f3}**:\n- {menu.part2.val3}")
            embed.set_thumbnail(url=client.avatar_url)
            embed.set_footer(text=client.footer_text, icon_url=client.avatar_url)
        except Exception as e:
            client.log.info(e)
            embed = discord.Embed(title=f"Error 404", description=f"**`•` `{date.replace('-', '/')}/{year}` Le CROUS ne fournit pas d'information actuellement pour ce restaurant...**", color=client.color, url=infos.url)

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