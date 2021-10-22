# general constants
DRIVER_PATH = r".\chromedriver.exe"
SITE_URL = r"https://www.olx.pl/"

# main filter data
CITIES_LIST = ["Katowice", "Chorzów", "Ruda Śląska", "Siemianowice Śląskie", "Świętochłowice", "Mysłowice"]
FLAT_CATEGORY = "Sprzedaż"                      # designed for "Sprzedaż" only
PRICE_FROM = "120000"                           # type: int or None
PRICE_TO = "320000"                             # type: int
AREA_FROM = "45"                                # type: int
AREA_TO = None                                  # type: int or None
ROOM_NUMBER = ["3 pokoje", "4 i więcej"]        # possible options: "1 pokój", "2 pokoje", "3 pokoje", "4 i więcej"

# iteration data
SUBPAGE_LIMIT = None                            # for one city; must be int >= 1 or None