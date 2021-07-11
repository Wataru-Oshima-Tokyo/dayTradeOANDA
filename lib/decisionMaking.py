import datetime
import requests
from time import sleep
import re
import pandas as pd
import math 
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
from . import constVariables


def executeBuyOrSell(pcc, targethour):
    access_token = constVariables.CVAL.access_token
    accountID = constVariables.CVAL.accountID

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
    Order_units = orderUnits*25
    if (pcc<0):
        Order_units = -1* Order_units
        print("Bidで注文します")
    else:
        print("ASKで注文します")
    Pip_location = -2
    TP_pips = 11 #pips
    TP_distance = TP_pips * (10**Pip_location)
    SL_pips = 11 #pips
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
    
    timetowait = 1500

    while(timetowait>600):
        now = datetime.datetime.now()
        current_time = now.strftime("%H%M%S")
        print("We will determine the order after " + str(timetowait) + "s")
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
    return tdr

def readData(targethour):
    now = datetime.datetime.now()
    todays_date = str(now.strftime("%Y%m%d")) 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM data')
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
        rateOfWin = float(executeBuyOrSell(pcc, targethour))
    elif (pcc<0):
        pcc=-1
        rateOfWin = float(executeBuyOrSell(pcc, targethour))
    else: 
        print("not buy anything")
        sleep(900)
    return rateOfWin

def mainexecuting(targethour, now, todays_date):
    # 実行   
    pcc = readData(targethour)
    percent = bidOrAsk(pcc, targethour)
    if (percent !=0):
        writeResult(percent, now, todays_date)
