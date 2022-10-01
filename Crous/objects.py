from bs4 import BeautifulSoup


class Menu:
    def __init__(self, data: str):
        self.data = data

        if data.startswith("Le CROUS ne fournit pas d'information actuellement pour ce restaurant..."):
            self.error = True
        else:
            self.error = False

            self.tradi = Traditionnel(data)
            self.brasserie = Brasserie(data)

            self.dates = get_dates(data)
    

class Traditionnel:
    def __init__(self, data: str):
        self.entrees = get_list(data, 1)
        self.plats = get_list(data, 2)
        self.deserts = get_list(data, 3)

        self.entrees_format = '\n- '.join(self.entrees)
        self.plats_format = '\n- '.join(self.plats)
        self.deserts_format = '\n- '.join(self.deserts)

class Brasserie:
    def __init__(self, data: str):
        self.entrees = get_list(data, 4)
        self.plats = get_list(data, 5)
        self.deserts = get_list(data, 6)

        self.entrees_format = '\n- '.join(self.entrees)
        self.plats_format = '\n- '.join(self.plats)
        self.deserts_format = '\n- '.join(self.deserts)


def get_list(
    data: str, 
    index: int
):
    list_data = []
    for i in data.split("<h4>")[index].split('<li>'):
        list_data.append(' '.join(BeautifulSoup(i, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", ""))
    return list_data[1:]


def get_dates(
    data: str
):
    list_data = []
    for i in data.split("<h4>")[0].split('</a>'):
        txt = ' '.join(BeautifulSoup(i, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
        if ' ' in txt:
            txt = txt.split(' ')[1]
        list_data.append(txt)
    return list_data[:7]



class Info:
    def __init__(self, data: dict, coords: tuple):
        self.data = data

        self.url = data.get('url', '')
        self.campus = data.get('campus', '')
        self.nom = data.get('nom', '')
        self.adresse = data.get('adresse', '')
        self.cp = data.get('cp', '')
        self.ville = data.get('ville', '')
        self.tel = str(data.get('tel', '')).replace(".", " ")
        self.mail = data.get('mail', '')

        self.wifi = data.get('wifi', '')
        
        self.coords = coords

        self.horaires = Horaires(data.get('horaires', ''))
        self.payement = Payment(data.get('payement', ''))
        self.acces = Acces(data.get('acces', ''))


class Horaires:
    def __init__(self, data: dict):
        self.data = data

        self.midi_self = data.get('midi', {}).get('self', '')
        self.midi_cafet = data.get('midi', {}).get('cafet', '')


class Payment:
    def __init__(self, data: dict):
        self.data = data

        self.cb = data.get('cb', False)
        self.izly = data.get('izly', False)


class Acces:
    def __init__(self, data: dict):
        self.data = data

        self.pmr = data.get('pmr', False)
        self.bus = data.get('bus', [])