import datetime
import pytz
import oandapyV20.endpoints.instruments as instruments
import json
from oandapyV20 import API
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades
from time import sleep
import math
import requests
import pandas as pd
# local package
from  .WriteDBAndReport import writeResult, readDatafromresultDBandShowTheRateOfWin, get_connection
from . import sendEmailtoTheUser
from . import decisionMaking
from . import monitorExchangeRate

  
def orderConfirmation(orderList):
    buyStop = orderList[0]
    buyLimit = orderList[1]
    sellStop = orderList[2]
    sellLimit = orderList[3]
    n=0
    for i in orderList:
        price = float(i)
        if (price > 0):
            n+=1
    tradeId =[]
    if(n!=0):
        percent = math.floor(10/n)
        if(buyStop != 0):
            resultId = orderFlexible(buyStop, "BUY", "STOP", percent)
            print("逆指値買いの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(buyLimit != 0):
            resultId = orderFlexible(buyLimit, "BUY", "LIMIT", percent)
            print("指値買いの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(sellStop != 0):
            resultId = orderFlexible(sellStop, "SELL", "STOP", percent)
            print("逆指値売りの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
        if(sellLimit != 0):
            resultId = orderFlexible(sellLimit, "SELL", "LIMIT", percent)
            print("指値売りの注文が完了しました")
            if(resultId!=0):
                tradeId.append(resultId)
    return tradeId

def subExecuting():
    stopPrice = getCandlesForStopOredr()
    result = stopOrder(stopPrice)
    return result
    
def confirmResults(orderID, now, todays_date):
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    now = datetime.datetime.now()
    current_time = int(now.strftime("%M"))
    # 利益幅を確認する
    resultList=[]
    tradeIdList =[]
    for i in orderID:
        try:
            orderId = int(i)
            print(orderId)
            r = orders.OrderDetails( accountID ,orderID=orderId)
            CheckTradeId = api.request(r)
            tradeId = float(CheckTradeId['order']['tradeID'])
            resultList.apeend(tradeId)
        except:
            print('It was canceled')
            
    for i in tradeIdList:
        try:
            tr = orders.OrderDetails(accountID, tradeID=i)
            tradeDetail = api.request(tr)
            result = tradeDetail['trade']['realizedPL']
            resultList.append(result)
        except:
            pass
    for i in resultList:
            writeResult(i, now, todays_date)
    showResult = readDatafromresultDBandShowTheRateOfWin()
    title = "現在の勝率"
    sendEmailtoTheUser.main(showResult, title)
    
def stopOrder(limitPrice):
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
    orderUnits = 100
    Order_unitsForAsk = orderUnits*5
    Order_unitsForBid = -1*orderUnits*5
    highestPriceinTokyo = limitPrice[0]
    lowestPriceinTokyo = limitPrice[1]
    print(highestPriceinTokyo)
    print(lowestPriceinTokyo)
    Pip_location = -2
    TP_pips = 10 #pips
    SL_pips = 10 #pips
    cancelTime = datetime.datetime.utcnow()+ datetime.timedelta(hours = 4)
    cancelTime = monitorExchangeRate.timeModified(cancelTime)
    print("canceltime should be " +str(cancelTime))
    Highest_TP_distance = round(highestPriceinTokyo + TP_pips * (10**Pip_location),3)
    Highest_SL_distance = round(highestPriceinTokyo - SL_pips * (10**Pip_location),3)
    Lowest_TP_distance = round(lowestPriceinTokyo - TP_pips * (10**Pip_location),3)
    Lowest_SL_distance = round(lowestPriceinTokyo + SL_pips * (10**Pip_location),3)        

    data_MarketHigh = {
                    "order": {
                            "units": str(Order_unitsForAsk),
                            "price": str(highestPriceinTokyo),
                            "instrument": "USD_JPY",
                            "timeInForce": "GTD",
                            "gtdTime":str(cancelTime),
                            "type": "STOP",
                            "positionFill": "DEFAULT",
                            #TP
                            "takeProfitOnFill" : {
                                "price": str(Highest_TP_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }, 
                            #SL
                            "stopLossOnFill" : {
                                "price": str(Highest_SL_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }
                               
                            }
                    }  

    data_MarketLow = {
                    "order": {
                            "units": str(Order_unitsForBid),
                            "price": str(lowestPriceinTokyo),
                            "instrument": "USD_JPY",
                            "timeInForce": "GTD",
                            "gtdTime":str(cancelTime),
                            "type": "STOP",
                            "positionFill": "DEFAULT",
                            #TP
                            "takeProfitOnFill" : {
                                "price": str(Lowest_TP_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }, 
                            #SL
                            "stopLossOnFill" : {
                                "price": str(Lowest_SL_distance),
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                }   
                            }
                    }
    
    datahigh = json.dumps(data_MarketHigh)
    datalow = json.dumps(data_MarketLow)  
    try:
        # サーバーへの要求
        Response_BodyHigh = requests.post(url, headers=headers, data=datahigh)
        # エラー発生時に例外処理へ飛ばす
        Response_BodyHigh.raise_for_status()
        sleep(0.5)
        Response_BodyLow = requests.post(url, headers=headers, data=datalow)
        # エラー発生時に例外処理へ飛ばす
        Response_BodyLow.raise_for_status()  
        
        #結果の表示
        print("逆指値の注文が確定しました")
        orderIdList=[]
        idForHigh = json.dumps(Response_BodyHigh.json()['orderCreateTransaction']['id'])
        idForLow = json.dumps(Response_BodyLow.json()['orderCreateTransaction']['id'])
        print("オーダーIDは以下です")
        orderIdList.append(idForHigh)
        orderIdList.append(idForLow)
        print(orderIdList)
    #例外処理
    except Exception as e:
            if "Response_Body" in locals(): # or vars()
                    print("Status Error from Server(raise) : %s" %Response_BodyHigh.text)
                    print("Status Error from Server(raise) : %s" %Response_BodyLow.text)
            print("エラーが発生しました。\nError(e) : %s" %e)

    return orderIdList

def getCandlesForStopOredr():
    # I think I need to think of summer time and winter since this is started at 9 am in London
    bgOfTokyoMarket = datetime.datetime.utcnow()- datetime.timedelta(hours = 8)
    bgOfLondonMarket = datetime.datetime.utcnow()
    date_from =""
    date_to=""
        
    API_access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"
    # URLの設定　（デモ口座用非ストリーミングURL）
    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    
    date_from = monitorExchangeRate.timeModified(bgOfTokyoMarket)
    date_to = monitorExchangeRate.timeModified(bgOfLondonMarket)
    print("ターゲットタイム（UTC）は"+date_from + " to " + date_to)
    # <ろうそく足取得用URLの変数の設定>
    # /v3/instruments/{Account ID}/candles 
    count = 8
    url = API_URL + "/v3/instruments/%s/candles?count=%s&price=M&granularity=H1&smooth=True&from=%s" % (INSTRUMENT, count,date_from)
    # ヘッダー情報の変数の設定
    headers = {
                "Authorization" : "Bearer " + API_access_token
        }
    # サーバーへの要求
    response = requests.get(url, headers=headers)
    # 処理結果の編集
    Response_Body = response.json()
    # print(Response_Body)
    # print(json.dumps(Response_Body, indent=2))
    high =[]
    low =[]
    highestAndLowest =[]
    for i in range(count):
        high.append(float(Response_Body["candles"][i]["mid"]["h"]))
        low.append(float(Response_Body["candles"][i]["mid"]["l"]))
    high.sort()
    low.sort()
    highestAndLowest.append(high[count-1])
    highestAndLowest.append(low[0])
    # print(high)
    # print(low)
    # print(highestAndLowest)
    return highestAndLowest

def getShortAndLongCountPercent():
    access_token = "175cc666c9a97c267b957da004cc83eb-9e9d5b50095e0fd1cdc163f494a9472a"
    accountID = "101-001-18171827-001"

    api = API(access_token=access_token, environment="practice")

    r = instruments.InstrumentsOrderBook(instrument="USD_JPY")
    m = instruments.InstrumentsPositionBook(instrument="USD_JPY")
    positionBook = api.request(m)
    orderBook = api.request(r)
    df = pd.DataFrame(r.response["orderBook"]["buckets"])

    API_URL =  "https://api-fxpractice.oanda.com"
    # 通貨ペア
    INSTRUMENT = "USD_JPY"
    # <現在レートの取得用URLの変数の設定>
    # /v3/accounts/{Account ID}/pricing 
    url = API_URL + "/v3/accounts/%s/pricing?instruments=%s" % (str(accountID), INSTRUMENT)
    # ヘッダー情報の変数の設定
    headers = {
                    "Authorization" : "Bearer " + access_token
                }
    # サーバーへの要求
    response = requests.get(url, headers=headers)
    # 処理結果の編集
    Response_Body = json.loads(response.text)
    currentPrice = float(Response_Body["prices"][0]["bids"][0]["price"])
    targetPriceList = []
    shortOrderList = []
    longOrderList = []
    checked=""
    shortTargetPrice =[]
    longTargetPrice = []

    for i in range(len(df)):
        checked=orderBook['orderBook']['buckets'][i]['price']
        if(float(checked) >currentPrice -1):
            if (float(checked) <currentPrice+1):
                longCountPercentOrder = float(orderBook['orderBook']['buckets'][i]['longCountPercent'])
                shortCountPercentOrder = float(orderBook['orderBook']['buckets'][i]['shortCountPercent'])
                if (longCountPercentOrder >1):
                    longOrderList.append(orderBook['orderBook']['buckets'][i])
                    longTargetPrice.append(orderBook['orderBook']['buckets'][i]['price'])
                if (shortCountPercentOrder >1):
                    shortOrderList.append(orderBook['orderBook']['buckets'][i])
                    shortTargetPrice.append(orderBook['orderBook']['buckets'][i]['price'])

    buy_Stop = 0 #逆指値の買い（順ばり）
    buy_Limit = 0 #指値の買い（逆ばり）
    sell_Stop = 0 #逆指値の売り（順ばり）
    sell_Limit = 0 #指値の売り（逆ばり）
    for i in range(len(longTargetPrice)):
        if(float(longTargetPrice[i]) > currentPrice):
            buy_Stop = float(longTargetPrice[i]) 
            try:
                while(float(longTargetPrice[i]) >currentPrice):
                    i -=1
                buy_Limit = float(longTargetPrice[i]) 
            except:
                pass
            break
    if(buy_Stop == 0):
        try:
            longTargetPrice.sort(reverse=True)
            buy_Limit = float(longTargetPrice[0])
        except:
            pass

    for i in range(len(shortTargetPrice)):
        if(float(shortTargetPrice[i]) > currentPrice):
            sell_Limit = float(shortTargetPrice[i]) 
            try:
                while(float(shortTargetPrice[i]) > currentPrice):
                    i -= 1
                sell_Stop = float(shortTargetPrice[i]) 
            except:
                pass
            break
    if(sell_Stop == 0):
        try:
            shortTargetPrice.sort(reverse=True)
            sell_Limit = float(shortTargetPrice[0])
        except:
            pass
    targetPriceList.append(buy_Stop)
    targetPriceList.append(buy_Limit)
    targetPriceList.append(sell_Stop)
    targetPriceList.append(sell_Limit)
    print("The current price is "+ str(currentPrice) +". The short/long count percent is " + str(targetPriceList) +" (逆指値買い、指値買い、逆指値売り、指値売り)")
    return targetPriceList

def orderFlexible(target, buysell, stoplimit,percent):
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

    price = float(target)
    if(price !=0):
        Pip_location = -2
        TP_pips = 10 #pips
        SL_pips = 10 #pips
        if(buysell=="BUY"):
            orderUnits = orderUnits*percent
            TP_distance = round(price + TP_pips * (10**Pip_location),3)
            SL_distance = round(price - SL_pips * (10**Pip_location),3)
        else:
            orderUnits = -1*orderUnits*percent
            TP_distance = round(price - TP_pips * (10**Pip_location),3)
            SL_distance = round(price + SL_pips * (10**Pip_location),3)

        startTime = datetime.datetime.utcnow()
        startTime = int(startTime.strftime("%H"))
        finish = 4- (startTime%4)
        cancelTime = datetime.datetime.utcnow()+ datetime.timedelta(hours = finish)
        cancelTime = monitorExchangeRate.timeModified(cancelTime)
        print("canceltime should be " +str(cancelTime))
        if(stoplimit =="STOP"):
            typeOfOrder = "STOP"
        else:
            typeOfOrder = "LIMIT"

        data_Market = {
                        "order": {
                                "units": str(orderUnits),
                                "price": str(price),
                                "instrument": "USD_JPY",
                                "timeInForce": "GTD",
                                "gtdTime":str(cancelTime),
                                "type": typeOfOrder,
                                "positionFill": "DEFAULT",
                                #TP
                                "takeProfitOnFill" : {
                                    "price": str(TP_distance),
                                    "timeInForce": "GTD",
                                    "gtdTime":str(cancelTime),
                                    }, 
                                #SL
                                "stopLossOnFill" : {
                                    "price": str(SL_distance),
                                    "timeInForce": "GTD",
                                    "gtdTime":str(cancelTime),
                                    }   
                                }
                        }
        
        data = json.dumps(data_Market)
        orderId =''
        try:
            # サーバーへの要求
            Response_Body = requests.post(url, headers=headers, data=data)
            # エラー発生時に例外処理へ飛ばす
            Response_Body.raise_for_status()

            #結果の表示
            print("注文が確定しました")
            print(json.dumps(Response_Body.json(), indent=2))

            print("オーダーIDは以下です")
            orderIdList=[]
            orderId = json.dumps(Response_Body.json()['orderCreateTransaction']['id'])
            print(orderId)
        #例外処理
        except Exception as e:
                if "Response_Body" in locals(): # or vars()
                        print("Status Error from Server(raise) : %s" %Response_Body.text)
                
                print("エラーが発生しました。\nError(e) : %s" %e)
        return orderId

def job3():
    # 指値:逆指値注文用
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    tommorow = todays_date +1
    orderId = [] 
    timetowaitForsl =0
    flag =0
    while (todays_date != tommorow):
        japanTime = datetime.datetime.now()
        newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
        todays_date = str(japanTime.strftime("%Y%m%d"))  
        current_timeJ = int(japanTime.strftime("%H%M%S"))
        current_hour = int(japanTime.strftime("%H"))
        current_minute = int(japanTime.strftime("%M"))
         # 指値：逆指値を調べて１％以上注文が入っていたら注文を入れる(四時間ごとにチェック)
        if ((current_hour+2)%4 ==0):
            if (current_minute<2):
                timetowaitForsl = 0
                orderList = getShortAndLongCountPercent()
                stopLimitId = orderConfirmation(orderList)
                for i in stopLimitId:
                    orderId.append(i)
                timetowaitForsl = 14340
                sleep(60)
                flag = 1

        if (flag !=0):
            print("Stop or Limit function will be rebooted after " +str(timetowaitForsl) +"s")
            timetowaitForsl -=60
        else: 
            pass
        # 東京市場の高値：安値を調べて指値注文する
        if (londonTime.hour >= 9):
            if(londonTime.hour  <10):
                if(londonTime.minute <10):
                    eachId = subExecuting()
            try:
                orderId.append(eachId[0])
            except:
                orderId.append(0)
            try:
                orderId.append(eachId[1])
            except:
                orderId.append(0)
        print(str(current_timeJ) +": Cheking time for stop/limit order...")
        todays_date = int(japanTime.strftime("%Y%m%d")) 
        sleep(60)
    confirmResults(orderId, japanTime, todays_date)

  