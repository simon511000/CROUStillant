from bs4 import BeautifulSoup


class Menu:
    def __init__(self, data: str, format: dict):
        self.data = data

        if data.startswith("Le CROUS ne fournit pas d'information actuellement pour ce restaurant..."):
            raise AttributeError
        else:
            self.part1 = Part1(data, format)
            self.part2 = Part2(data, format)

            self.dates = get_dates(data)
    

class Part1:
    def __init__(self, data: str, format: dict):
        self.title = format.get(-1)


        self.f1 = format.get(0)
        self.val1 = '\n- '.join(get_list(data, 1))

        self.f2 = format.get(1)
        self.val2 = '\n- '.join(get_list(data, 2))

        self.f3 = format.get(2)
        self.val3 = '\n- '.join(get_list(data, 3))


class Part2:
    def __init__(self, data: str, format: dict):
        self.title = format.get(-3)


        self.f1 = format.get(0)
        self.val1 = '\n- '.join(get_list(data, 4))

        self.f2 = format.get(1)
        self.val2 = '\n- '.join(get_list(data, 5))

        self.f3 = format.get(2)
        self.val3 = '\n- '.join(get_list(data, 6))



def get_list(
    data: str, 
    index: int
):
    list_data = []
    for i in data.split("<h4>")[index].split('<li>'):
        txt = ' '.join(BeautifulSoup(i, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
        if txt != "":
            list_data.append(txt)
    return list_data[1:]


def get_dates(
    data: str
):
    list_data = []
    for i in data.split("<h4>")[0].split('</a>'):
        txt = ' '.join(BeautifulSoup(i, "html.parser").findAll(text=True)).replace(" \n", "").replace("\n", "")
        if ' ' in txt:
            txt = txt.split(' ')[1]
        if "-" in txt:
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
        self.paiement = Paiement(data.get('paiement', ''))
        self.acces = Acces(data.get('acces', ''))


class Horaires:
    def __init__(self, data: dict):
        self.data = data

        self.midi_self = data.get('midi', {}).get('self', '')
        self.midi_cafet = data.get('midi', {}).get('cafet', '')


class Paiement:
    def __init__(self, data: dict):
        self.data = data

        self.cb = data.get('cb', False)
        self.izly = data.get('izly', False)


class Acces:
    def __init__(self, data: dict):
        self.data = data

        self.pmr = data.get('pmr', False)
        self.bus = data.get('bus', [])