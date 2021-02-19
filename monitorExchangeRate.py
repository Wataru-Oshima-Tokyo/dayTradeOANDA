import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import time
import math
from datetime import datetime
from WriteDBAndReport import readDatafromdataDB, createAndWriteDB
# class monitorExchangeRate:



def extract():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
    url = 'https://info.finance.yahoo.co.jp/fx/detail/?code=usdjpy'
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup,exr,ts, num):
    Rate = soup.find('dd', id = 'USDJPY_detail_bid').text.strip()
    try:
        RateInt =float(Rate)
        exr.append(RateInt)
        ts.append(num)
    except:
        num -= 1
        print("cannot convert from rateInt to int")
    return num
    

def pearsonCorrelationCoeffcient(classList):
    print("")
    x = classList.x
    y = classList.y
    xn = len(x)
    yn = len(y)
    xtotal = 0
    ytotal = 0
    for i in range(xn):
        xtotal +=x[i-1]
        ytotal +=y[i-1]
        xavg = xtotal/xn
        yavg = ytotal/yn
        numerator = 0
    for i in range(xn):
        xi = x[i-1]
        yi =y[i-1]
        numerator += (xi-xavg )*(yi-yavg)
        denominatorLeft =0
        denominatorRight =0
        denominator = 0
    for i in range(xn):
        xi = x[i-1]
        yi =y[i-1]
        denominatorLeft += (xi-xavg )*(xi-xavg )
        denominatorRight += (yi-xavg )*(yi-xavg )
        denominator = math.sqrt(denominatorLeft*denominatorRight)
    #     print("denominator is " +str(denominator))
    try:
        r = float (numerator/denominator)*100
        print("The pearson correlation coeffcient is " + str(r))
    except:
        r = 0
        print(r)
    return r



def job1():
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d"))
    exchangeRate =[]
    timeSpent =[]
    class elementList:
        x = exchangeRate
        y = timeSpent
    print("Gathering information", end="")
    target_date = int(now.strftime("%Y%m%d")) +1
    todays_dateInt =int(todays_date)
    i= int(now.strftime("%M"))*20
    overtime =i
    while (todays_dateInt != target_date):
        now = datetime.now()
        todays_dateInt =int(now.strftime("%Y%m%d"))
        i+=1
        c=extract()
        passedTime = i - overtime
        i = transform(c, exchangeRate, timeSpent, passedTime) + overtime
        print(i)
        if (i%1200==0):
            result = pearsonCorrelationCoeffcient(elementList)
            createAndWriteDB(result)
            readDatafromdataDB()
            i=0
            exchangeRate =[]
            timeSpent =[]
            now = datetime.now()
            current_time = int(now.strftime("%M"))
            elementList.x =exchangeRate
            elementList.y = timeSpent
            if(current_time > 40):
                timetowait = (60 -int(current_time))*60
                time.sleep(timetowait)
            elif(current_time <10):
                overtime = current_time*20
                i = overtime
        else:
            time.sleep(2.7)
