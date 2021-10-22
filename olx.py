from advertParent import AdvertParentClass
import re

class OlxClass(AdvertParentClass):
    def setTitle(self):
        self.title = self.soup.find(attrs={"data-cy": 'ad_title'}).contents[0]

    def setPrice(self):
        self.price = float ( self.soup.find(attrs={"data-testid": "ad-price-container"}).h3.contents[0].replace("zł", "").replace(" ", "").replace(",", ".") )

    def setPricePerM2(self):
        perM2Text = self.soup.find_all(string=re.compile("^Cena za"))[0]
        self.pricePerM2 = float ( re.search("(\D+)(\d+[.]?\d*)(\D*)", perM2Text).group(2) )

    def setArea(self):
        areaText = self.soup.find_all(string=re.compile("^Powierzchnia"))[0]
        self.area = float ( re.search("(\D+)(\d+[,.]?\d*)(\D*)", areaText).group(2).replace(",", ".") )

    def setNumberOfRooms(self):
        numberOfRoomsText = self.soup.find_all(string=re.compile("^Liczba"))[0]
        self.numberOfRooms = int ( re.search("(\D+)(\d+)(\D*)", numberOfRoomsText).group(2) )

    def setDescr(self):
        self.descr = (self.soup.find(attrs={"data-cy": "ad_description"})).text.replace("\n", " ").replace("\t", " ").replace("/", "\\")