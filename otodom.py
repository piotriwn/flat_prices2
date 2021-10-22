from advertParent import AdvertParentClass

class OtodomClass(AdvertParentClass):
    def setTitle(self):
        self.title = self.soup.find(attrs={"data-cy": "adPageAdTitle"}).contents[0]

    def setPrice(self):
        self.price = float ( self.soup.find(attrs={"aria-label": 'Cena'}).contents[0].strip("zł").replace(" ", "").replace(",", ".") )

    def setPricePerM2(self):
        self.pricePerM2 = float ( self.soup.find(attrs={"aria-label": "Cena za metr kwadratowy"}).contents[0].replace("zł/m²", "").replace(" ", "") )

    def setArea(self):
        self.area = float ( self.soup.find(attrs={"aria-label": "Powierzchnia"}).find_all("div")[-1].contents[0].replace("m²", "").replace(" ", "").replace(",", ".") )

    def setNumberOfRooms(self):
        self.numberOfRooms = int ( self.soup.find(attrs={"aria-label": "Liczba pokoi"}).find_all("div")[-1].contents[0].replace(" ", "") )

    def setDescr(self):
        self.descr = (self.soup.find(attrs={"data-cy": "adPageAdDescription"})).text.replace("\n", " ").replace("\t", " ").replace("/", "\\")