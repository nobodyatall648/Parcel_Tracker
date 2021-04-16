#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from lxml import etree
from tabulate import tabulate
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

        print("[*] Initializing Chrome Driver")
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
                trackingRsl = []                                                                              
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
                    
                    #append each result into trackingRsl List
                    trackingRsl.append([str(trackingDate), str(trackingTime), str(trackingInfo), str(trackingLocation)])                                       

                #print tracking details table
                print("Tracking Code: " + trackingID, end="\n\n")
                print(tabulate(trackingRsl, headers=['Date', 'Time', 'Status', 'Location']), end="\n\n")                                  
            else:
                checkNoRecord = driver.find_element_by_xpath('//div[@class="noRecordsText"]')
                print("[!] " + checkNoRecord.get_attribute('innerHTML'), end="\n\n")
                sys.exit()                                         
        else:
            print('[!] TrackingList Class Not Found.', end="\n\n")
        
    except WebDriverException:
        print('[!] Browser Window Closed.')
        sys.exit(0)
    except Exception as e:
        print('[!] Something Went Wrong Here!')
        print(e)
        sys.exit()
    finally:
        driver.close()

def jtexpress(trackingCode):
    trackingURL = "https://www.jtexpress.my/track.php?awbs=" + trackingCode

    requestRet = requests.get(trackingURL)
    
    if(requestRet.status_code == 200):
        try:
            print("[*] Checking: " + trackingCode)
            soup = BeautifulSoup(requestRet.text,'html.parser')               
            trackingResult = soup.findAll("div", {"class": "tracking-result-box-right-inner"})                        

            trackingRsl = []
            for i in range(len(trackingResult)):                
                #extracking tracking contents from the page
                soup = BeautifulSoup(str(trackingResult[i]),'html.parser')
                trackingDate = soup.find("div", {"class" : "tracking-point-date-time tracking-date"})
                trackingTime = soup.findAll("div", {"class" : "tracking-point-date-time"})
                
                if(i==0):
                    trackingDetails = soup.find("div", {"class" : "tracking-point-details latest-scanning"})
                else:
                    trackingDetails = soup.find("div", {"class" : "tracking-point-details"})          

                #reformat the output
                trackingDateArr = str(trackingDate).split('\n') 
                trackingDate = trackingDateArr[1].replace('<div>','').replace('</div>','') + " "
                trackingDate += trackingDateArr[2].replace('<div>','').replace('</div>','')

                trackingTimeArr = str(trackingTime[1]).split('\n')
                trackingTime = trackingTimeArr[1].replace('</div>', '').strip()

                trackingDetailArr = str(trackingDetails).split('<br/>')
                trackingInfo = trackingDetailArr[0].split('\n')[1].strip()
                trackingCity = trackingDetailArr[1].replace('City :', '').strip()
                trackingStatus = trackingDetailArr[2].replace('Status : <span style="color:;">', '').replace('Status : <span style="color:green;">', '').replace('</span> </div>', '').strip()
                                  
                #append each result into trackingRsl List
                trackingRsl.append([str(trackingDate), str(trackingTime), str(trackingInfo), str(trackingCity), str(trackingStatus)])                                       
                
            
            #check there's result or not          
            if(len(trackingRsl) == 0):
                print("[!] No Result Found.", end="\n\n")
            else:                        
                #print tracking result in table
                print("[*] Check complete print result: ", end="\n\n")
                print("Tracking Code: " + trackingCode, end="\n\n")
                print(tabulate(trackingRsl, headers=['Date', 'Time', 'Info', 'City', 'Status']), end="\n\n") 

        except Exception as e:
            print("[!] Something Went Wrong Here.")
            print(e)
            sys.exit(0)
    else:
        print('[!] ERROR Occured!')
        print("[!] Status Code: " + str(requestRet.status_code))
        sys.exit(0)
                   

    

def helpMenu():
    print('format: python3 parcelTracker.py <courier company> <tracking code>', end='\n\n')
    print('Courier Company: ')
    print('1) Pos Laju')
    print('2) J&T Express')
    
def main():
    if(len(sys.argv) != 3):
        helpMenu()
        sys.exit(0)
    
    courier = int(sys.argv[1])
    trackingCode = sys.argv[2]

    if(courier == 1):        
        poslaju(trackingCode)
    elif(courier == 2):
        jtexpress(trackingCode)
    else:
        print("[!] Invalid Courier.")

if __name__ == "__main__":
    main()