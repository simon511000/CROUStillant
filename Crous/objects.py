class RU:
    """
    Main Class - RU - Resto U
    
    Data:
    - ru.dates
    - ru.menu
    - ru.info
    """
    def __init__(self, data: dict, dates: list, rdata: dict):
        self.data = data

        self.dates = dates
        self.menus = Menus(data, dates)
        self.info = Info(rdata)
        

#############################################


class Menus:
    def __init__(self, data: dict, dates: list):
        self.data = data
        self.dates = dates

        self.count = len(data)


    def __iter__(self):
        self.index = -1
        return self


    def __next__(self):
        if self.index >= len(self.data) - 1:
            raise StopIteration

        self.index += 1

        return Repas(self.data[self.dates[self.index]], self.dates[self.index])


class Repas:
    def __init__(self, data: dict, date: str):
        self.data = data

        self.date = date

        self.matin = Categories(data.get("Petit déjeuner"))
        if self.matin.categories == []:
            self.matin = data.get("Petit déjeuner")

        self.midi = Categories(data.get("Déjeuner"))
        if self.midi.categories == []:
            self.midi = data.get("Déjeuner")

        self.soir = Categories(data.get("Dîner"))
        if self.soir.categories == []:
            self.soir = data.get("Dîner")


class Categories:
    def __init__(self, data: dict):
        self.data = data

        try:
            self.categories = list(self.data.keys())
        except AttributeError:
            self.categories = []


    def __iter__(self):
        self.index = -1
        return self


    def __next__(self):
        if isinstance(self.data, str):
            raise StopIteration
        else:
            if self.index >= len(self.data) - 1:
                raise StopIteration

            self.index += 1

        return Categorie(self.data[self.categories[self.index]], self.categories[self.index])


class Categorie:
    def __init__(self, data: dict, categorie: str):
        self.data = data

        self.categorie = categorie


#############################################


class Info:
    def __init__(self, data: dict):
        self.data = data

        self.url = data.get('url')
        self.type = data.get('type', '')
        self.zone = data.get('campus', '')
        self.nom = data.get('nom', '')
        self.adresse = data.get('adresse', '')
        self.cp = data.get('cp', '')
        self.ville = data.get('ville', '')
        self.tel = str(data.get('tel', '')).replace(".", " ")
        self.mail = data.get('mail', '')

        self.wifi = data.get('wifi', '')
        
        self.coords = Coords(data.get('geolocalisation'))

        self.horaires = Horaires(data.get('horaires', ''))
        self.paiement = Paiement(data.get('paiement', ''))
        self.acces = Acces(data.get('acces', ''))


class Coords:
    def __init__(self, data: dict):
        self.data = data

        self.lat = data.get('lat')
        self.long = data.get('long')


class Horaires:
    def __init__(self, data: dict):
        self.data = data

        self.midi_self = data.get('self', '')
        self.midi_cafet = data.get('cafet', '')


class Paiement:
    def __init__(self, data: dict):
        self.data = data

        self.cb = data.get('cb')
        self.izly = data.get('izly')


class Acces:
    def __init__(self, data: dict):
        self.data = data

        self.bus = data.get('bus', [])
        self.tram = data.get('tram', [])
        self.pmr = data.get('pmr')