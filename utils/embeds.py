from Crous.objects import RU

from utils.data import icons


import discord


import datetime
import pytz


def get_clean_date(day, month, year):
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembtre", "octobre", "novembre", "décembre"]

    date = pytz.timezone("Europe/Paris").localize(datetime.datetime(int(year), int(month), int(day)), is_dst=None)

    return f"{jours[int(date.strftime('%w'))-1]} {day} {mois[int(date.strftime('%m'))-1]}"


async def load_embed(client, data: RU):
    embeds = []
    options = []
    
    if data.info.acces.bus == []:
        bus = ""
    else:
        bus = f"\n╰ {icons['bus']} **Bus**: `{', '.join(data.info.acces.bus)}`"

    if data.info.acces.pmr == []:
        pmr = ""
    else:
        pmr = f"\n╰ {icons['pmr']} **PMR**: `Accessible aux personnes à mobilité réduite`"

    if data.info.wifi:
        wifi = f"\n**`•` {icons['wifi']} Wifi**: `Disponible`"
    else:
        wifi = ""

    if data.info.paiement.izly:
        izly = f"\n**`•` {icons['izly']} IZLY**: `Disponible`"
    else:
        izly = ""

    if data.info.paiement.cb:
        cb = f"\n**`•` {icons['cb']} Carte Bancaire**: `Disponible`"
    else:
        cb = ""
    
    if data.info.horaires.midi_cafet != "":
        cafet = f"\n╰ **Cafétéria**: `{data.info.horaires.midi_cafet}`"
    else:
        cafet = ""
    
    default=discord.Embed(title=f"{data.info.nom}", description=f"**`•` Campus**: `{data.info.campus}`\n**`•` Adresse**: `{data.info.adresse}, {data.info.cp} {data.info.ville}`{wifi}\n\n**`•` Téléphone**: `{data.info.tel}`\n**`•` Courriel**: `{data.info.mail}`", color=client.color, url=data.info.url)
    default.add_field(name=f"Horraires:", value=f"╰ **Self**: `{data.info.horaires.midi_self}`{cafet}")
    default.add_field(name=f"Paiements:", value=f"{cb}{izly}", inline=False)
    default.add_field(name=f"Accès:", value=f"{bus}{pmr}", inline=False)
    default.set_thumbnail(url=client.avatar_url)
    default.add_field(url=f"https://data.enseignementsup-recherche.gouv.fr/explore/embed/dataset/fr_crous_restauration_france_entiere/map/?location=18,{data.info.coords.lat},{data.info.coords.long}&basemap=mapbox.streets")
    default.set_footer(text=client.footer_text, icon_url=client.avatar_url)
   
        
    if len(data.dates) == 0:
        embed = discord.Embed(title=f"{data.info.nom} - Error 404", description=f"**`•` Le CROUS ne fournit pas d'information actuellement pour ce restaurant...**\n**`•` Mis à jour**: <t:{int(datetime.datetime.utcnow().timestamp())}:R> (<t:{int(datetime.datetime.utcnow().timestamp())}>)", color=client.color, url=data.info.url)
        embed.set_footer(text=client.footer_text, icon_url=client.avatar_url)
        embeds.append(embed)
        options.append(discord.SelectOption(label="Indisponible...", description=f"{data.info.nom}", value=0, default=True))
    else:
        paris_dt = pytz.timezone("Europe/Paris").localize(datetime.datetime.now(), is_dst=None)

        index = 0

        for menu in data.menus:
            pass_menu = False
            embed = None

            for i in range(1, 4): # Check Week-ends because sometimes Friday's menu is still displayeds
                new_dt = paris_dt - datetime.timedelta(days=i) 
                if get_clean_date(int(new_dt.strftime("%d")), int(new_dt.strftime("%m")), int(new_dt.strftime("%Y"))) == menu.date:
                    pass_menu = True
            
            if not pass_menu:
                if not embed:
                    embed = discord.Embed(title=f"{data.info.nom}", description=f"**`•` Menu du `{str(menu.date).title()}`**\n**`•` Mis à jour**: <t:{int(datetime.datetime.utcnow().timestamp())}:R> (<t:{int(datetime.datetime.utcnow().timestamp())}>)\n\u2063", color=client.color, url=data.info.url)

                if isinstance(menu.midi, str):
                    embed.add_field(name=f"\u2063", value=f"**{menu.midi}**")
                else:
                    count = 0
                    msg = ""

                    for i in menu.midi:
                        msg += f"**{i.categorie}**\n{'\n- '.join(i.data)}\n"
                        count += 1

                        if count == 3:
                            embed.add_field(name=f"\u2063", value=msg)
                            embed.add_field(name="ㅤㅤ", value="ㅤㅤ")
                            msg = ""

                    if msg == "":
                        embed.add_field(name=f"\u2063", value=msg)
                        embed.add_field(name="ㅤㅤ", value="ㅤㅤ")
                        msg = ""
                            
            
            embed.set_footer(text=client.footer_text, icon_url=client.avatar_url)
            embeds.append(embed)
            options.append(discord.SelectOption(label=str(menu.date).title(), description=f"{data.info.zone} - {data.info.nom}", value=index, default=True if index == 0 else False))
            
            index += 1

    if len(embeds) == 0:
        embed = discord.Embed(title=f"{data.info.nom} - Error 404", description=f"**`•` Le CROUS ne fournit pas d'information actuellement pour ce restaurant...**\n**`•` Mis à jour**: <t:{int(datetime.datetime.utcnow().timestamp())}:R> (<t:{int(datetime.datetime.utcnow().timestamp())}>)", color=client.color, url=data.info.url)
        embed.set_footer(text=client.footer_text, icon_url=client.avatar_url)
        embeds.append(embed)
        options.append(discord.SelectOption(label="Indisponible...", description=f"{data.info.nom}", value=0, default=True))


    return (embeds, options, default)