from .objects import RU


from aiohttp import ClientSession
from bs4 import BeautifulSoup
from pathlib import Path
import json

path = str(Path(__file__).parents[0].parents[0])


async def get_menu(session: ClientSession, rid: str):
    with open(f"{path}/data.json", "r") as f:
        config = json.load(f)
    rdata = config[rid]


    async with session.get(rdata.get('url')) as response:
        text = await response.text()

    soup = BeautifulSoup(text, "html.parser")
    results = soup.find(id="menu-repas")
    elements = results.find_all("ul", class_="slides")
    elements = str(elements[0])
    elements = elements.split("<h3>")
    elements.pop(0) # remove: <ul class="slides">


    dates = []
    data = {}

    for elt in elements:
        selt = elt.split("</h3>")
        date = selt[0].replace("Menu du ", "")[:-5]
        dates.append(date)

        data[date] = {}

        for x in selt[1:]:
            sselt = x.split("<h4>")

            for y in sselt[1:]:
                ssselt = y.split("</h4>")
                header = ssselt[0]

                data[date][header] = {}

                for z in ssselt[1:]:
                    if not "li" in z.split('\n')[0]:
                        data[date][header] = ''.join(BeautifulSoup(z, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
                    else:
                        sdata = z.split("<span class=\"name\">")

                        for a in sdata[1:]:
                            sssselt = a.split("</span><ul class=\"liste-plats\">")
                            title = sssselt[0]

                            menus = []
                            for b in sssselt[1].split('</li>'):
                                n = ''.join(BeautifulSoup(b, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
                                if n != '':
                                    menus.append(n)

                            data[date][header][title] = menus
        
    return RU(data, dates, rdata)