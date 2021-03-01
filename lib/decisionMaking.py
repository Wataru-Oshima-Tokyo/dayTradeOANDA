import datetime
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
import chromedriver_binary
import os
import json
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades
#local package
from  .WriteDBAndReport import writeResult, readDatafromresultDBandShowTheRateOfWin, get_connection
from . import sendEmailtoTheUser


def executeBuyOrSell(pcc, targethour):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = accounts.AccountSummary(accountID)
    acc = api.request(r)
    orderUnits = acc['account']['balance']

    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
        
    # 注文用URLの変数の設定 その１
    url = API_URL + "/v3/accounts/%s/orders" % str(accountID)
    
    # ヘッダー情報の変数の設定
    headers = {
                "Content-Type" : "application/json", 
                "Authorization" : "Bearer " + access_token
            }  
    
    # #データ情報の変数の設定
    try:
        orderUnits = float(orderUnits)
        orderUnits =math.floor(orderUnits)
    except:
        orderUnits = 1
    Order_units = orderUnits*5
    if (pcc<0):
        Order_units = -1* Order_units
        print("Bidで注文します")
    else:
        print("ASKで注文します")
    Pip_location = -2
    TP_pips = 10 #pips
    TP_distance = TP_pips * (10**Pip_location)
    SL_pips = 10 #pips
    SL_distance = SL_pips * (10**Pip_location)         
    
    data_Market = {
                    "order": {
                            "units": Order_units,
                            "instrument": "USD_JPY",
                            "timeInForce": "FOK",
                            "type": "MARKET",
                            "positionFill": "DEFAULT",
                            #SL
                            "stopLossOnFill" : {
                                    "distance": str(SL_distance),
                                    "timeInForce": "GTC" 
                                    },
                            }
                    }  
    
    data = json.dumps(data_Market)
        
    try:
        # サーバーへの要求
        Response_Body = requests.post(url, headers=headers, data=data)
        # エラー発生時に例外処理へ飛ばす
        Response_Body.raise_for_status()
                
        #約定されたトレード情報の取得
        #トレードID
        Trade_no = str(Response_Body.json()['orderFillTransaction']['tradeOpened']['tradeID'])
        #売買判定
        Trade_units = float(Response_Body.json()['orderFillTransaction']['tradeOpened']['units'])
        #約定価格
        Trade_price = float(Response_Body.json()['orderFillTransaction']['tradeOpened']['price'])

        #TPプライスの計算  
        if Trade_units > 0: 
                TP_price = Trade_price + TP_distance         
        else:
                TP_price = Trade_price - TP_distance         
        TP_price = round(TP_price, 3)  

        # トレード変更用URL変数の設定
        url = API_URL + "/v3/accounts/%s/trades/%s/orders" % (str(accountID), Trade_no)
            
        # データ情報の変数の設定
        data_Modify = {
                    #TP
                        "takeProfit" : {
                                "price": str(TP_price),
                                "timeInForce": "GTC"  
                                },
                        }

        data = json.dumps(data_Modify)
        Response_Body = requests.put(url, headers=headers, data=data)
        # エラー発生時に例外処理へ飛ばす
        Response_Body.raise_for_status()
            
        #結果の表示
        print("注文が確定しました")
        print(json.dumps(Response_Body.json(), indent=2))

    #例外処理
    except Exception as e:
            if "Response_Body" in locals(): # or vars()
                    print("Status Error from Server(raise) : %s" %Response_Body.text)
            
            print("エラーが発生しました。\nError(e) : %s" %e)
    
    timetowait = 0
    if (targethour == "h14"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h21"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
    elif (targethour == "h01"):
        now = datetime.datetime.now()
        timetowait = (60 - int(now.strftime("%M")))*60
        timetowait += 10800
    else:
        timetowait =1500

    while(timetowait>600):
        now = datetime.datetime.now()
        current_time = now.strftime("%H%M%S")
        print("We will determine the order after" + str(timetowait) + "s")
        sleep(600)
        timetowait -=600

    sleep(timetowait)

    # 指定時間後に自動決済
    try:
        r = trades.TradeClose(accountID ,tradeID=Trade_no)
        api.request(r)
        print("約定が確定しました")
    except:
        print("すでに約定しています")
    sleep(2)
    # 利益幅を確認する
    try:
        r = trades.TradeDetails(accountID ,tradeID=Trade_no)
        tradeDetail = api.request(r)
        tdr =tradeDetail["trade"]["realizedPL"]
    except:
        tdr = 0
    
    now = datetime.datetime.now()
    current_time = int(now.strftime("%M"))
    timetowait = 0
    if(current_time > 0):
        timetowait = (60 -int(current_time))*60
    else:
        timetowait = 3600
    print("I will wati for " + str(timetowait) +"s")
    while timetowait >600:
        timetowait -=600
        print("Market order function will be rebooted after" +str(timetowait) +"s.")
        sleep(600)
        now = datetime.datetime.now()
        current_time = int(now.strftime("%M"))
        if (current_time <= 10):
            timetowait = 0
            break
    sleep(timetowait)
    return tdr


def readDataForInverse(targethour):
    overallPcc = 0
    eachPcc = 0
    if (targethour == "h14"):
        now = datetime.datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 10
        dividedby = 0
        for row in cur:
            if (row[1] == todays_date):
                total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                        print("conversion sucess!!")
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        cur.close()
        conn.close()
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc   
    elif (targethour=="h21"):
        now = datetime.datetime.now()
        todays_date = str(now.strftime("%Y%m%d")) 
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 18
        dividedby = 0
        for row in cur:
        #you can modify here h13 ->sth
            if (row[1] == todays_date):
                total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                        print("conversion sucess!!")
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        cur.close()
        conn.close()
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc   
    elif (targethour=="h01"):
        now = datetime.datetime.now()
        todays_date = int(now.strftime("%Y%m%d")) -1
        todays_date = str(todays_date)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM data')
        start = 23
        dividedby = 0
        for row in cur:
        #you can modify here h13 ->sth
            if (row[1] == todays_date):
                if (start >=24):
                    total = "h" + str(start-24)
                    now = datetime.datetime.now()
                    todays_date = str(now.strftime("%Y%m%d")) 
                else:
                    total = "h" + str(start)
                if (row[2] ==total):
                    start +=1
                    dividedby +=1
                    try:
                        eachPcc = float(row[3])
                    except:
                        eachPcc =0
                    overallPcc += eachPcc
                else:
                    pass
            else:
                pass
        try:
            overallPcc = -1*(overallPcc/dividedby)
        except:
            overallPcc = 0
        cur.close()
        conn.close()
        print("The total pcc is from " + str(dividedby) + " hours ago to now is " +  str(overallPcc))
        return overallPcc
    else:
        pass 


def readData(targethour):
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    # dbをpandasで読み出す。
    # df = pd.read_sql('SELECT * FROM data', conn)
    cur.execute('SELECT * FROM data')
    # print(cur.fetchall())
    pcc60min =0.0
    for row in cur:
        if(todays_date == row[1]):
            if (row[2] ==targethour):
                # pcc60min = str(row[3])
                try:
                    pcc60min = float(row[3])
                    msg = "conversion sucess!! : " + str(pcc60min)
                    print(msg)
                    break
                except:
                    pcc60min = 0  
            else:
                pcc60min = 0  
        else:
            pass
    cur.close()
    conn.close()
    return pcc60min


def bidOrAsk(pcc, targethour):
    rateOfWin = 0
    pcc = float(pcc)
    # I guess that you can modify the percent here as you see the pcc
    if (pcc>0):
        pcc =1
        rateOfWin = executeBuyOrSell(pcc, targethour)
    elif (pcc<0):
        pcc=-1
        rateOfWin = executeBuyOrSell(pcc, targethour)
    else: 
        print("not buy anything")
        sleep(900)
    return rateOfWin

def mainexecuting(targethour, now, todays_date):
    # 実行   
    if (targethour =="h14"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h21"):
        pcc = readDataForInverse(targethour)
    elif(targethour =="h01"):
        pcc = readDataForInverse(targethour)
    else:
        pcc = readData(targethour)
    percent = bidOrAsk(pcc, targethour)
    if (percent !=0):
        writeResult(percent, now, todays_date)
        showResult = readDatafromresultDBandShowTheRateOfWin()
        title = "現在の勝率"
        sendEmailtoTheUser.main(showResult, title)

def temp():
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    mainexecuting('h17', now, todays_date)
