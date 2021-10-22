from constants import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By    
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import getpass
import os
import sys
import time
from bs4 import BeautifulSoup as soup
import requests
from otodom import OtodomClass
from olx import OlxClass
import re
import csv

class MainProgram:
    def __init__(self):
        self.log = ""
        self.driverExt = webdriver.ChromeOptions()
        self.driverExt.add_extension('ublock.crx')
        self.driver = webdriver.Chrome(DRIVER_PATH, chrome_options=self.driverExt)
        
        self.mainFilterURL = None
        self.currentPage = 1
        self.linkScrappingBool = True
        self.URLsList = []
        self.OlxList = []
        self.OtodomList = []
        self.leftoverList = []

        self.outputDict = {}

    def execute(self):
        if (self._reachRealEstatePage() ):
            for city in CITIES_LIST:
                if (not self._fillCriteriaOneCity(city)):
                    self.linkScrappingBool = False
                    continue
                if (not self._iterateOneCity(city)):
                    self.linkScrappingBool = False
                    continue

            if (not self.linkScrappingBool):
                self._printAndLog(f"There were issues scrapping URLs. Do you want to continue [y] to gather data from adverts anyway?\n")
                answer = input()
                if (answer not in ("y", "Y", "yes", "Yes")):
                    self._logToFile()
                    sys.exit()

            self._printAndLog("\n\n---------------------\n\n")
            self._printAndLog(f"Attempting to scrape data from gathered links.\n")
            self._divideListBetweenOlxOtodom()
            i = 1
            for link in self.OlxList:
                OlxObj = OlxClass(link[1], link[0])
                if (not self._setAdvertObjectContent(OlxObj) ):
                    continue
                self._setAdvertObjectProperties(OlxObj)
                self._printAndLog("--\n")
                self.outputDict[i] = OlxObj.outputToDict()
                i += 1
            for link in self.OtodomList:
                OtodomObj = OtodomClass(link[1], link[0])
                if (not self._setAdvertObjectContent(OtodomObj) ):
                    continue
                self._setAdvertObjectProperties(OtodomObj)
                self._printAndLog("--\n")
                self.outputDict[i] = OtodomObj.outputToDict()
                i += 1
            self._outputToCSV()
            print(self.URLsList)
            print(self.outputDict)
            self._logToFile()
        else:
            self._printAndLog("Could not reach real estate Olx page.\n")
            sys.exit()

    def _reachRealEstatePage(self):
        self._printAndLog("Attempting to reach OLX.pl site...\n")
        self.driver.get(SITE_URL)

        self._printAndLog("Checking if there's cookies' prompt to accept...\n")

        cookiesPrompt = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@id="onetrust-banner-sdk"]')))
        if (cookiesPrompt != []):
            if (not self._acceptCookies()):
                return False
            time.sleep(2)
            self.driver.get(SITE_URL)
        else:
            self._printAndLog("No cookies to accept, proceeding... ")
        time.sleep(1)
        self._printAndLog("Attempting to confirm we've landed on OLX.pl page...\n")
        try:
            metaSiteName = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/head/meta[@content="OLX.pl"]')))
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self._printAndLog("Attempting to click on real estate icon... ")
        try:
            realEstateA = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="maincategories-list clr"]//a[.//span[text()="Nieruchomości"]]')))
            realEstateA.click()
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        time.sleep(2)
        self._printAndLog("Attempting to click on flats link... ")
        try:
            flatsA = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="subcategories-list clr"]//a[.//span[text()="Mieszkania"]]')))
            flatsA.click()
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self.mainFilterURL = self.driver.current_url
        if (not self._confirmLandingOnPage(1) ):
            return False
        return True

    def _acceptCookies(self):
        self._printAndLog("Attempting to accept cookies' prompt... ")
        try:
            cookiesAcceptButton = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@id="onetrust-banner-sdk"]//button[@id="onetrust-accept-btn-handler"]')))
            cookiesAcceptButton.click()
        except Exception as e:
            self._standardException(e, quit=True)
        self._printAndLog("Successully landed on real estate page.\n")
        return True

    def _fillCriteria(self, city):
        self._printAndLog("Attempting to fill in criteria...\n")
        self._printAndLog(f"Attempting to fill in city {city}... ")
        time.sleep(5)
        try:
            cityInput = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//input[@id="cityField"]')))
            cityInput.send_keys(city)
            time.sleep(2)
            cityInput.send_keys(Keys.TAB)
            time.sleep(2)
            cityInputFilled = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@id="cityFieldGray"]//span[contains (text(), "{0}") ]'.format(city))))
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self._printAndLog(f"Attempting to fill in offer category {FLAT_CATEGORY}... ")
        try:
            offerCategoryLi = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "clr multifilters subSelectActive")]//li[.//div[text()="Wybierz kategorię"]]')))
            offerCategoryDiv = WebDriverWait(offerCategoryLi, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "filter-item rel category-item")]')))
            offerCategoryA = WebDriverWait(offerCategoryDiv, 5).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@class, "button gray block category rel zi3 clr")]')))
            offerCategoryA.click()
            time.sleep(0.5)
            offerCategorySelected = WebDriverWait(offerCategoryDiv, 5).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Sprzedaż"]')))
            offerCategorySelected.click()
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self._printAndLog(f"Attempting to set price from {PRICE_FROM} to {PRICE_TO}... " if PRICE_FROM else f"Attempting to set price to {PRICE_TO}... ")
        try:
            if (PRICE_FROM):
                priceFromInputSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "price")]//div[contains(@class, "filter-item-from")]//span[contains(@class, "header block")]')))
                priceFromInputSpan.click()
                self.driver.implicitly_wait(5)
                priceFromA = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/header/div[3]/div/form/noindex/div/fieldset[2]/ul/li[2]/ul/li/div[2]/div[1]/a')))
                priceFromA.click()
                self.driver.implicitly_wait(5)
                priceFromInput = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//li[contains(@data-key, "price")]//input[contains(@class, "min-value-input")]')))
                ActionChains(self.driver).move_to_element(priceFromInput).send_keys(PRICE_FROM).perform()
            priceToInputSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "price")]//div[contains(@class, "filter-item-to")]//span[contains(@class, "header block")]')))
            priceToInputSpan.click()
            self.driver.implicitly_wait(5)
            priceToA = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/header/div[3]/div/form/noindex/div/fieldset[2]/ul/li[2]/ul/li/div[2]/div[2]/a')))
            priceToA.click()
            self.driver.implicitly_wait(5)
            priceToInput = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//li[contains(@data-key, "price")]//input[contains(@class, "max-value-input")]')))
            ActionChains(self.driver).move_to_element(priceToInput).send_keys(PRICE_TO).perform()
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self._printAndLog(f"Attempting to set area from {AREA_FROM} to {AREA_TO}... " if AREA_TO else f"Attempting to set area from {AREA_FROM}... ")
        try:
            areaFromSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "m")]//div[contains(@class, "filter-item-from")]//span[contains(@class, "header block")]')))
            areaFromSpan.click()
            areaFromInput = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "m")]//input[contains(@class, "min-value-input")]')))
            areaFromInput.click()
            areaFromInput.send_keys(AREA_FROM)
            time.sleep(2)
            if (AREA_TO):
                areaToSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "m")]//div[contains(@class, "filter-item-to")]//span[contains(@class, "header block")]')))
                areaToSpan.click()
                areaTo = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "m")]//input[contains(@class, "max-value-input")]')))
                areaTo.send_keys(AREA_TO)
                time.sleep(2)
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        roomNumbersStr = "Attempting to choose the following number of rooms: " + ", ".join(ROOM_NUMBER) + "... "
        self._printAndLog(roomNumbersStr)
        try:
            roomsSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "rooms")]//div[contains(@class, "filter-item-rooms")]//span[contains(@class, "header block")]')))
            roomsSpan.click()
            for item in ROOM_NUMBER:
                roomItemLi = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//li[contains(@data-key, "rooms")]//li[.//span[contains(text(), "{0}" )]]'.format(item))))
                roomItemTick = WebDriverWait(roomItemLi, 5).until(EC.presence_of_element_located((By.XPATH, './/span[contains(@class, "multichbox__icon")]')))
                roomItemTick.click()
            time.sleep(2)
            self._printAndLog("Success.\n")
            self._printAndLog("---------------------\n\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        return True

    def _confirmLandingOnPage(self, pageNumber):
        self._printAndLog(f"Attempting to confirm landing on subpage {pageNumber}... ")
        time.sleep(3)
        try:
            metaSiteName = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '/html/head/meta[@content="OLX.pl"]')))
            pageCurrentSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "pager")]//span[@data-cy="page-link-current"]')))
            pageCurrentSpanText = WebDriverWait(pageCurrentSpan, 5).until(EC.presence_of_element_located((By.XPATH, './/span'))).text
            if ( int(pageCurrentSpanText) != pageNumber ):
                raise Exception(f"Expected page number {pageNumber} not equal to scrapped page number {int(pageCurrentSpanText)}. ")
            self._printAndLog("Success.\n")
            self._printAndLog("---------------------\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        return True

    def _scrapeLinksFromSubpage(self, city):
        self._printAndLog("Attempting to scrape links from subpage... ")
        try: 
            linkAElements = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, '//a[(contains(@class, "link")) and (contains(@data-cy, "listing-ad-title"))]')))
            for AElements in linkAElements:
                tpl = (city, AElements.get_attribute("href"))
                self.URLsList.append(tpl)
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        return True

    def _goToNextSubpage(self):
        self._printAndLog("Attempting to click on next subpage's link... ")
        try:
            nextPageSpan =  WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "fbold next")]')))
            nextPageA = WebDriverWait(nextPageSpan, 5).until(EC.presence_of_element_located((By.XPATH, './/a[contains(@data-cy, "page-link-next")]')))
            nextPageA.click()
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        return True

    def _checkIfNextPageByLimit(self):
        if (not SUBPAGE_LIMIT):
            return True
        self._printAndLog(f"Currently on page {self.currentPage}. Checking if we have room to go until {SUBPAGE_LIMIT}... ")
        self._printAndLog(f"{self.currentPage}/{SUBPAGE_LIMIT}. ")
        if (self.currentPage >= SUBPAGE_LIMIT):
            self._printAndLog("NO, can't go further as per the limit.\n")
            return False
        else:
            self._printAndLog("YES, can go further as per the limit.\n")
            return True

    def _checkIfNextPageByAvailability(self):
        self._printAndLog(f"Checking if there are subpages available...\n")
        self._printAndLog(f"Locating next page <span> tag... ")
        try:
            pagerDiv = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "pager rel")]')))
        except:
            self._printAndLog(f"The page does not have a pager <div>, therefore cannot go further.\n")
            return False
        try:
            nextPageSpan = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "fbold next")]')))
            self._printAndLog("Success.\n")
        except Exception as e:
            return self._standardException(e, quit=True)
        self._printAndLog(f"Checking if <span> tag contains <a> tag... ")
        try:
            nextPageA = WebDriverWait(nextPageSpan, 5).until(EC.presence_of_element_located((By.XPATH, './/a')))
            self._printAndLog("YES, there are pages available.\n")
        except Exception as e:
            return self._standardException(e, msg ="NO, there are no pages available.\n", quit=False)

    def _checkBothAvailabilities(self):
        byLimit = self._checkIfNextPageByLimit()
        if (byLimit):
            byAvail = self._checkIfNextPageByAvailability()
            if (byAvail):
                return True
        return False

    def _iterateThroughSubpages(self, city):
        self._printAndLog("Iterating through subpages in city {city}...\n\n")
        # 1. while - check if we should go to the next page 
        # 2. scrape links from current page (we start from page1)
        # 3. break if error scraping, otherwise continue
        # 4. go to the next page
        # 5. break if error going to next subpage, otherwise continue
        # 6. confirm if we landed
        # 7. break if error landing, otherwise continue
        # 8. increment current page counter
        # 9. calculate if we should go to next page - first based on limit, then based on availability
        successIter = True
        while (self._checkBothAvailabilities()):                                # ad.1, ad.9
            successIter = False
            if (not self._scrapeLinksFromSubpage(city)):                            # ad.2
                break                                                           # ad.3
            if (not self._goToNextSubpage() ):                                  # ad.4
                break                                                           # ad.5
            if (not self._confirmLandingOnPage( self.currentPage + 1 ) ):       # ad.6
                break                                                           # ad.7
            self.currentPage += 1                                               # ad.8
            successIter = True
        # last iteration (I know I've written it ugly, I'll hope to revisit it sometime later)
        successIter = successIter and ( self._scrapeLinksFromSubpage(city) )
        self._printAndLog("---------------------\n")
        if (successIter):
            self._printAndLog("Finished iterating through subpages successfully.\n")
            return True
        else:
            self._printAndLog("Did NOT finish iterating through subpages successfully.\n")
            return False

    def _fillCriteriaOneCity(self, city):
        self.currentPage = 1
        self.driver.get(self.mainFilterURL)
        time.sleep(2)
        if (self._fillCriteria(city) ):
            self._printAndLog(f"Criteria for city {city} filled successfully.\n")
            return True
        else:
            self._printAndLog(f"Could not fill criteria for city {city}.\n")
            return False

    def _iterateOneCity(self, city):
        if (self._iterateThroughSubpages(city) ):
            self._printAndLog(f"Scrapping links for city {city} finished successfully\n")
            self._printAndLog("--\n")
            return True
        else:
            self._printAndLog(f"There were some issues scrapping links for city {city}.\n")
            self._printAndLog("--\n")
            return False
    
    def _divideListBetweenOlxOtodom(self):
        for element in self.URLsList:
            if ( element[1].startswith("https://www.olx.pl") ):
                self.OlxList.append(element)
            elif ( element[1].startswith("https://www.otodom.pl") ):
                self.OtodomList.append(element)
            else:
                self.leftoverList.append(element)

    def _setAdvertObjectContent(self, obj):
        self._printAndLog(f"Attemping to set advert object with an URL of {obj.url} site data... ")
        try:
            obj.setPage()
        except Exception as e:
            return self._standardException(e, msg=f"Could not get site data for an object.\n")
        try:
            obj.setPageContents()
        except Exception as e:
            return self._standardException(e, msg=f"Could not get site content for an object.\n") 
        try:
            obj.setSoup()
        except Exception as e:
            return self._standardException(e, msg=f"Could not create a soup for an object.\n") 
        self._printAndLog(f"Success.\n")
        return True

    def _setAdvertObjectProperties(self, obj):
        self._printAndLog(f"Attemping to set fields of object with an URL of {obj.url}... ")
        allClear = True
        try:
            obj.setTitle()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set title for an object.\n")
        try:
            obj.setPrice()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set price for an object.\n")
        try:
            obj.setPricePerM2()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set price for a square meter for an object.\n")
        try:
            obj.setArea()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set area for an object.\n")
        try:
            obj.setNumberOfRooms()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set number of rooms for an object.\n")
        try:
            obj.setDescr()
        except Exception as e:
            allClear = self._standardException(e, msg=f"Could not set description for an object.\n")
        if (allClear):
            self._printAndLog("Success.\n")
            return True
        else:
            self._printAndLog("Failed. Some fields could not be set\n")
            return False

    def _printAndLog(self, msg):
        self.log += msg
        print(msg)

    def _standardException(self, ex, msg = "Failed.\n", quit = False, returnBool = True):
        line = f"{msg}{str(ex)}\n"
        print(line)
        self.log += line
        if (quit):
            self.driver.quit()
        if (returnBool):
            return False

    def _outputToCSV(self):
        filename = datetime.now().strftime(r"%d_%m_%Y_%H_%M_%S") + "_" + getpass.getuser() + "_data.csv"
        pathname = os.path.abspath(os.path.dirname(__file__))
        filePath = os.path.join(pathname , 'Results' , filename)
        with open(filePath, mode='w', newline='', encoding="utf-8-sig") as results:
            resultsWriter = csv.writer(results, delimiter="\t", quoting=csv.QUOTE_NONE, escapechar='\\')
            resultsWriter.writerow( ["#Offer","Title", "City", "URL", "Price", "PricePerM2", "Area", "#Rooms", "Description"] ) 
            for key, val in self.outputDict.items():
                resultsWriter.writerow([key, val["title"], val["city"], val["url"], val["price"], val["pricePerM2"], val["area"], val["rooms"], val["descr"]  ])

    def _logToFile(self):
        filename = datetime.now().strftime(r"%d_%m_%Y_%H_%M_%S") + "_" + getpass.getuser() + ".txt"
        pathname = os.path.abspath(os.path.dirname(__file__))
        filePath = os.path.join(pathname , 'Logs' , filename)    
        with open (filePath , "w") as f:
            f.write(self.log)

def main():
    program = MainProgram()
    program.execute()


if __name__== "__main__":
    main()