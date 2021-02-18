from datetime import datetime
from time import sleep
import re
import csv
import pandas as pd
import math 
import sqlite3
import threading

#custom import
import decisionmaking
import dbtocsv


todays_date ="0"
while (todays_date != "20220218"):
    now = datetime.now()
    todays_date = str(now.strftime("%Y%m%d"))  
    #10時の東京市場順張りチェック
    current_time = int(now.strftime("%H%M%S"))
    if (current_time >= 100500):
        if(current_time <=110500):
            decisionmaking.mainexecuting("h10", now, todays_date)
        elif(current_time <=120500):
            decisionmaking.mainexecuting("h11", now, todays_date)
        elif(current_time <=130500):
            decisionmaking.mainexecuting("h12", now, todays_date)
        elif(current_time <=134500):
            decisionmaking.mainexecuting("h13", now, todays_date)
        else:
            pass
    else:
        pass
    #15時の東京市場逆張りチェック
    if (current_time >= 140500):
        if (current_time <= 142500):
            decisionmaking.mainexecuting("h14", now, todays_date)

        else:
            pass
    else:
        pass       

    #18時のロンドン市場順張りチェック
    if (current_time >= 180500):
        if(current_time <=190500):
            decisionmaking.mainexecuting("h18", now, todays_date)
        elif(current_time <=200500):
            decisionmaking.mainexecuting("h19", now, todays_date)
        elif(current_time <=204500):
            decisionmaking.mainexecuting("h20", now, todays_date)
        else:
            pass
    else:
        pass

    #21時のロンドン市場逆張りチェック
    if (current_time >= 210500):
        if (current_time <= 212500):
            decisionmaking.mainexecuting("h21", now, todays_date)
        else:
            pass
    else:
        pass 
    #25時のニューヨーク市場逆張りチェック
    if (current_time >= 500):
        if (current_time <= 1500):
            decisionmaking.mainexecuting("h01", now, todays_date)
        else:
            pass
    else:
        pass 

    print(current_time)
    sleep(5)
