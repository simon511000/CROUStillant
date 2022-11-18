from .objects import Menu, Info

from utils.data import restos_data, coords

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def load_dates(
    session: ClientSession,
    ru: str, 
    dt: str,
):
    data = {
        "ru": ru,
        "dt": dt    
    }
        
    async with session.post(f"https://ent-1.univ-reims.fr/esup-crous/action/getMenu.php", data=data) as response:
        text = await response.text()

        list_data = []
        for i in text.split("<h4>")[0].split('</a>'):
            txt = ' '.join(BeautifulSoup(i, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
            if ' ' in txt and '-' in txt:
                txt = txt.split(' ')[1]
            list_data.append(txt)
        return list_data[:7]


async def get_crous_menu(
    session: ClientSession,
    ru: str, 
    dt: str,
):
    data = {
        "ru": ru,
        "dt": dt    
    }
        
    async with session.post(f"https://ent-1.univ-reims.fr/esup-crous/action/getMenu.php", data=data) as response:
        text = await response.text()
        return Menu(text, restos_data.get(ru, {}).get('format'))


def get_crous_info(
    ru: str,
):
    return Info(restos_data[ru], coords[ru])