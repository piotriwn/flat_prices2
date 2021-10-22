import requests
from bs4 import BeautifulSoup as soup

class AdvertParentClass:
    def __init__(self, url, city):
        self.url = url
        self.page = None
        self.pageContent = None
        self.soup = None
        self.title = None
        self.city = city
        self.price = None
        self.pricePerM2 = None
        self.area = None
        self.numberOfRooms = None
        self.descr = None
        self.dict = {}
    
    def setPage(self):
        self.page = requests.get(self.url)

    def setPageContents(self):
        self.pageContent = self.page.content

    def setSoup(self):
        self.soup = soup(self.page.content, 'html.parser')

    def outputToDict(self):
        self.dict["title"] = self.title
        self.dict["city"] = self.city
        self.dict["url"] = self.url
        self.dict["price"] = self.price
        self.dict["pricePerM2"] = self.pricePerM2
        self.dict["area"] = self.area
        self.dict["rooms"] = self.numberOfRooms
        self.dict["descr"] = self.descr
        return self.dict