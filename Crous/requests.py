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
    results = soup.find("section", class_="menus")
    elements = results.find_all("div", class_="menu")


    dates = []
    data = {}

    for elt in elements:
        meal = str(elt).split('<time class="menu_date_title">')[1].split('</time>')


        # Get Date
        date = meal[0].replace("Menu du ", "")[:-5]
        dates.append(date)
        data[date] = {}


        meal = str(meal[1]).split('<div class="meal_title">')[1].split('</div>')


        # Get Header (e.g. 'Déjeuner')
        header = meal[0]
        data[date][header] = {}


        temp = ""
        menus = []
        for meal_data in meal[1].split('<li>')[1:]:
            if meal_data.endswith('<ul>'):
                if temp != "":
                    data[date][header][title] = menus
                    menus = []

                title = meal_data[:-4]
                temp = title  
            else:
                menus.append(''.join(BeautifulSoup(meal_data, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", ""))

        # We musn't forget the last one!
        data[date][header][title] = menus
        
        
    return RU(data, dates, rdata)
