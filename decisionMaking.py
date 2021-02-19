from datetime import datetime
from selenium import webdriver
import lxml
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from time import sleep
import re
import pandas as pd
import math 
from  .WriteDBAndReport import writeResult, readDatafromresultDBandShowTheRateOfWin, get_connection
import .sendEmailtoTheUser


def readDataForInverse(targethour):
    overallPcc = 0
    if (targethour == "h14"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 10
        for row in cur:
            if (row[1] == todays_date):
                if (start <=13):
                    total = "h" + str(start)
                    start +=1
                    if (row[2] ==total):
                        print(row[3])
                        overallPcc = str(row[3])
                        try:
                            overallPcc += float(overallPcc)
                            print("conversion sucess!!")
                        except:
                            overallPcc = 0 
                            break 
                    else:
                        break
                else:
                    break
            else:
                pass
        cur.close()
        conn.close()
        overallPcc = -1*(overallPcc/5)
        print(overallPcc)
        return overallPcc   
    elif (targethour=="h21"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 18
        while (start <= 21):
        #you can modify here h13 ->sth
            total = "h" + str(start)
            start +=1
            if (row[1] == todays_date):
                if (row[2] ==total):
                    overallPcc = str(row[3])
                    try:
                        overallPcc += float(overallPcc)
                        print("conversion sucess!!")
                    except:
                        overallPcc = 0 
                        break 
                else:
                    break
            else:
                pass
        overallPcc = -1*(overallPcc/4)
        cur.close()
        conn.close()
        return overallPcc   
    elif (targethour=="h01"):
        now = datetime.now()
        todays_date = int(now.strftime("%Y%m%d")) -1
        todays_date = str(todays_date)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 23
        while (start <= 25):
        #you can modify here h13 ->sth
            if (start >=24):
                total = "h" + str(start-24)
                now = datetime.now()
                todays_date = str(now.strftime("%Y%m%d")) 
            else:
                total = "h" + str(start)
            start +=1
            if (row[1] == todays_date):
                if (row[2] ==total):
                    overallPcc = str(row[3])
                    try:
                        overallPcc += float(overallPcc)
                        print("conversion sucess!!")
                    except:
                        overallPcc = 0 
                        break 
                else:
                    break
            else:
                pass
        overallPcc = -1*(overallPcc/3)
        cur.close()
        conn.close()
        return overallPcc
    else:
        pass 

def readData(targethour):
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    for row in cur:
        #you can modify here h13 ->sth
        if (row[2] ==targethour):
            pcc60min = str(row[3])
            try:
                pcc60min = float(pcc60min)
                msg = "conversion sucess!! : " + str(pcc60min)
                print(msg)
                break
            except:
                pcc60min = 0  
        else:
            pcc60min = 0  
    cur.close()
    conn.close()
    return pcc60min

def login(browser, un, pwd):
    browser.implicitly_wait(10)
    username_element = browser.find_element_by_id('accountId')
    username_element.send_keys(un)
    username_element = browser.find_element_by_id('password')
    username_element.send_keys(pwd)
    username_element = browser.find_element_by_id('LoginWindowBtn').click()
    browser.implicitly_wait(10)
    browser.implicitly_wait(10)
    window_after = browser.window_handles[1]
    browser.switch_to.window(window_after)
    sleep(5)
    # paegSource = browser.page_source

def controlBrowser(dm, targethour):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    url = 'https://demotrade.fx.dmm.com/fxcrichpresen/webrich/direct/login'
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    username = 'wataruoshima@my.smccd.edu'
    password = 'Ichiro0705'
    browser.get(url)
    print('ブラウザを起動しました')
    login(browser, username, password)
    print('ログインが完了しました')
    timeStart = 0
    if(dm==1):
        try:
            clickAsk = browser.find_element_by_xpath("//div[@uifield = 'askStreamingButton']").click()
            print("ASKを選択し、注文が完了しました")
        except:
            print("we cannot find ASK")
            enterAction = ActionChains(browser)
            tabAction = ActionChains(browser)
            tabAction.send_keys(Keys.RETURN)
            tabAction.perform()
            enterAction.perform()
            sleep(1)
            tabAction.perform()
            enterAction.perform()
            timeStart = 900
    elif (dm==-1):
        try:
            clickBid = browser.find_element_by_xpath("//div[@uifield = 'bidStreamingButton']").click()
            print("BIDを選択し、注文が完了しました")
        except:
            print("we cannot find BID")
            enterAction = ActionChains(browser)
            tabAction = ActionChains(browser)
            tabAction.send_keys(Keys.RETURN)
            tabAction.perform()
            enterAction.perform()
            sleep(1)
            tabAction.perform()
            enterAction.perform()
            timeStart = 900
    else :
        print("not buy/sell this time")
        timeStart = 900
    
    sleep(0.5)
    timetowait = 0
    if (targethour == "h14"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h21"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h01"):
        now = datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    else:
        timetowait =900

    while (timeStart <900):
        sleep(1)
        timeStart +=1
        searchpips = browser.find_element_by_xpath("//span[@uifield = 'evaluationPips']").text.strip()
        try:
            searchpips = float(searchpips)
        except:
            searchpips =0
        if (searchpips >= 10.0):
            break
        elif (searchpips <= -10.0):
            break
        else:
            continue
    try:
        clickclose = browser.find_element_by_xpath("//button[@uifield = 'quickCloseOrderButton']").click()
        actions = ActionChains(browser)
        nextaction = ActionChains(browser)
        nextaction.send_keys(Keys.RETURN)
        actions.send_keys(Keys.TAB)
        actions.perform()
        actions.perform()
        sleep(0.5)
        nextaction.perform()
        print("決済が完了しました")
    except:
        print("it is already closed")
    sleep(2)    
    browser.quit()
    return searchpips

def bidOrAsk(pcc, targethour):
    rateOfWin = 0
    # I guess that you can modify the percent here as you see the pcc
    if (pcc>0):
        pcc =1
        rateOfWin = controlBrowser(pcc, targethour)
    elif (pcc<0):
        pcc=-1
        rateOfWin = controlBrowser(pcc, targethour)
    else: 
        print("not buy anything")
        sleep(900)
    return rateOfWin

def mainexecuting(targethour, now, todays_date):
    # 実行   
    if (targethour =="h15"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h21"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h01"):
        pcc = readDataForInverse(targethour)
    else:
        pcc = readData(targethour)
    percent = bidOrAsk(pcc, targethour)
    writeResult(percent, now, todays_date)
    showResult = readDatafromresultDBandShowTheRateOfWin()
    title = "現在の勝率"
    sendEmailtoTheUser.main(showResult, title)

def temp():
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    mainexecuting('h17', now, todays_date)
