from datetime import datetime
import datetime
import pytz
from time import sleep
import re
import csv
import pandas as pd
import math 
from threading import Thread
import lib
from apscheduler.schedulers.blocking import BlockingScheduler 

def job2():
    sleep(120)
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    finishTime = int(japanTime.strftime("%H")) 
    while (finishTime != 7):
        japanTime = datetime.datetime.now()
        tokyoTime = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
        newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
        todays_date = str(japanTime.strftime("%Y%m%d"))  
        current_timeJ = int(japanTime.strftime("%H%M%S"))
        #10時の東京市場順張りチェック
        if (tokyoTime.hour >= 10):
            if (tokyoTime.hour <= 10):
                if(tokyoTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h10", japanTime, todays_date)
            elif(tokyoTime.hour <=11):
                if(tokyoTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h11", japanTime, todays_date)
                    
            elif(tokyoTime.hour <=12):
                if(tokyoTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h12", japanTime, todays_date)
                    
            elif(tokyoTime.hour <=13):
                if(tokyoTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h13", japanTime, todays_date)
                    
            else:
                pass
        else:
            pass
        #15時の東京市場逆張りチェック
        if (current_timeJ >= 140500):
            if (current_timeJ <= 141000):
                lib.decisionMaking.mainexecuting("h14", japanTime, todays_date)
            else:
                pass
        else:
            pass       
        
        #18時のロンドン市場順張りチェック
        if (londonTime.hour >= 10):
            if(londonTime.hour <=10):
                if(londonTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h18", japanTime, todays_date)
                    
            elif(londonTime.hour <=11):
                if(londonTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h19", japanTime, todays_date)
                    
            elif(londonTime.hour <=12):
                if (londonTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h20", japanTime, todays_date)
            else:
                pass
        else:
            pass

        #21時のロンドン市場逆張りチェック
        if (londonTime.hour >= 13):
            if(londonTime.hour <=13):
                if (londonTime.minute < 10):
                    lib.decisionMaking.mainexecuting("h21", japanTime, todays_date)
            else:
                pass
        else:
            pass 

        #22時のニューヨーク市場順張りチェック
        if (newyorkTime.hour >= 10):
            if(newyorkTime.hour  <=10):
                if(newyorkTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h22", japanTime, todays_date)
                    
            elif(newyorkTime.hour <=11):
                if(newyorkTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h23", japanTime, todays_date)
                    
            elif(newyorkTime.hour <=12):
                if (newyorkTime.minute <=10):
                    lib.decisionMaking.mainexecuting("h24", japanTime, todays_date)
                    
            else:
                pass
        else:
            pass

        # 25時のニューヨーク市場逆張りチェック
        if (newyorkTime.hour >= 13):
            if(newyorkTime.hour <=13):
                if (newyorkTime.minute < 10):
                    lib.decisionMaking.mainexecuting("h01", japanTime, todays_date)
                else:
                    pass
        else:
            pass 

        print(str(current_timeJ) +": Checking time for market order...")
        finishTime = int(japanTime.strftime("%H")) 
        sleep(60)


def letsGetStarted():
    jobfirst = Thread(target=lib.monitorExchangeRate.job1)
    jobsecond = Thread(target=job2)
    jobthird = Thread(target=lib.stopOrLimitOrder.job3)
    jobfirst.start()
    jobsecond.start()
    jobthird.start()



sched = BlockingScheduler()
# # Schedules job_function to be run from mon to fri
sched.add_job(letsGetStarted, 'cron',  day_of_week='mon-fri', hour=7, minute=5)
sched.start()