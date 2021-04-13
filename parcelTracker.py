#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import requests
import time
import sys

def poslaju(trackingCode):
    domainLink = "https://www.pos.com.my/"
    trackingID = trackingCode
    

    try:
        #chrome driver arguments
        driverOptions = webdriver.ChromeOptions()
        driverOptions.add_argument("--headless")    #hide chrome windows popup
        driverOptions.add_experimental_option("excludeSwitches", ["enable-logging"])

        driver = webdriver.Chrome(options=driverOptions)        
        driver.get(domainLink)
        actions = ActionChains(driver)

        print("[*] Start Checking Tracking Code: " + str(trackingID))
        selTrackCode = driver.find_element_by_xpath('//ul[@class="trackList home-widget-ui"]//li[1]')        
        actions.click(selTrackCode).perform()

        inputTrackCode = driver.find_element_by_xpath('//textarea[@id="w3mission"]')
        inputTrackCode.clear()
        inputTrackCode.send_keys(trackingID)
        
        print("[*] Checking: " + str(trackingID))        
        trackingCodeSubmit = driver.find_element_by_xpath('//button[@class="homeTrackSearchButton"]')
        trackingCodeSubmit.click()

        #check trackingItem class present
        checkTrackingListPresent = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, "//div[@class=\"trackingList\"]"))
        )

        if(checkTrackingListPresent):
            #get tracking details from trackingItem class 
            trackingList = driver.find_elements_by_xpath('//div[@class="trackingItem"]')

            if(len(trackingList) != 0):
                print("[*] Check complete print result:", end="\n\n")        

                #check trackingItem class existing (no tracking code found)                                                        
                          
                for i in range(len(trackingList)):
                    soup = BeautifulSoup(trackingList[i].get_attribute('innerHTML'), 'html.parser')
                    trackingDateTime = soup.findAll("div", {"class": "trackingDate"})
                    trackingContent = soup.findAll("div", {"class": "trackingContent"})
                    trackingLocation = soup.findAll("span", {"class": "spanLocation"})
                    
                    #reformating the result
                    trackingDate = str(trackingDateTime).split('<span>')[1].replace('</span>', '')
                    trackingTime = str(trackingDateTime).split('<span>')[2].replace('</div>', '').replace('</span>]', '')
                    trackingInfo = str(trackingContent).split('<span>')[1].split('</span>')[0]
                    trackingLocation = str(trackingLocation).split('class="spanLocation">')[1].split('</span>')[0]

                    print("Tracking Date: " + str(trackingDate) + "\tTracking Time: " + str(trackingTime))                    
                    print("Status: " + str(trackingInfo) + "\tLocation: " + str(trackingLocation), end='\n\n')
                                  
            else:
                checkNoRecord = driver.find_element_by_xpath('//div[@class="noRecordsText"]')
                print("[!] " + checkNoRecord.get_attribute('innerHTML'))
                sys.exit()                                         
        else:
            print('[!] TrackingList Class Not Found.')
        
    except WebDriverException:
        print('[!] Browser Window Closed.')
        sys.exit(0)
    except Exception as e:
        print('[!] Something Went Wrong Here!')
        print(e)
        sys.exit()
    finally:
        driver.close()

def helpMenu():
    print('format: python3 parcelTracker.py <courier company> <tracking code>', end='\n\n')
    print('Courier Company: ')
    print('1) Pos Laju')
    
def main():
    if(len(sys.argv) != 3):
        helpMenu()
        sys.exit(0)
    
    courier = int(sys.argv[1])
    trackingCode = sys.argv[2]

    if(courier == 1):        
        poslaju(trackingCode)
    else:
        print("[!] Invalid Courier.")

if __name__ == "__main__":
    main()