from datetime import datetime
from time import sleep
import re
import csv
import pandas as pd
import math 
from threading import Thread
import sampledesu.decisionMaking
import sampledesu.monitorExchangeRate

def job2():
    todays_date ="0"
    while (todays_date != "20220219"):
        now = datetime.now()
        todays_date = str(now.strftime("%Y%m%d"))  
        #10時の東京市場順張りチェック
        current_time = int(now.strftime("%H%M%S"))
        if (current_time >= 100500):
            if(current_time <=110000):
                decisionMaking.mainexecuting("h10", now, todays_date)
            elif(current_time <=120000):
                decisionMaking.mainexecuting("h11", now, todays_date)
            elif(current_time <=130000):
                decisionMaking.mainexecuting("h12", now, todays_date)
            elif(current_time <=134500):
                decisionMaking.mainexecuting("h13", now, todays_date)
            else:
                pass
        else:
            pass
        #15時の東京市場逆張りチェック
        if (current_time >= 140500):
            if (current_time <= 142500):
                decisionMaking.mainexecuting("h14", now, todays_date)
            else:
                pass
        else:
            pass       

        #18時のロンドン市場順張りチェック
        if (current_time >= 180500):
            if(current_time <=190000):
                decisionMaking.mainexecuting("h18", now, todays_date)
            elif(current_time <=200000):
                decisionMaking.mainexecuting("h19", now, todays_date)
            elif(current_time <=204500):
                decisionMaking.mainexecuting("h20", now, todays_date)
            else:
                pass
        else:
            pass

        #21時のロンドン市場逆張りチェック
        if (current_time >= 210500):
            if (current_time <= 212500):
                decisionMaking.mainexecuting("h21", now, todays_date)
            else:
                pass
        else:
            pass 
        # 25時のニューヨーク市場逆張りチェック
        if (current_time >= 500):
            if (current_time <= 1500):
                decisionMaking.mainexecuting("h01", now, todays_date)
            else:
                pass
        else:
            pass 

        print(current_time)
        sleep(5)

job1 = Thread(target=monitorExchangeRate.job1)
job2 = Thread(target=job2)
job1.start()
job2.start()
