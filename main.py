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

def getTargetHour(date):
    now = date
    todays_date = str(now.strftime("%Y%m%d"))
    targetTime =  int(now.strftime("%H"))
    # 日付data.dbを作成する
    # すでに存在していれば、それにアスセスする。
    if(targetTime <10):
        current_time = 'h0' + str(targetTime)
    else:
        current_time = 'h' + str(targetTime)
    return current_time

def job2():
    # sleep(120)
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    finishTime = 0; 
    flag = False
    while (finishTime != 7):
        japanTime = datetime.datetime.now()
        tokyoTime = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
        todays_date = str(japanTime.strftime("%Y%m%d"))  
        current_timeJ = int(japanTime.strftime("%H%M%S"))
        current_minute = int(japanTime.strftime("%M"))
        if(current_timeJ > 100000):
            flag = True
        if (flag):
            finishTime =int(japanTime.strftime("%H"))
        #順ばり
        if(current_minute <=5):
            target = getTargetHour(japanTime)
            lib.decisionMaking.mainexecuting(target, japanTime, todays_date)

        print(str(current_timeJ) +": Checking time for market order...")
        sleep(60)


def letsGetStarted():
    jobfirst = Thread(target=lib.monitorExchangeRate.job1)
    jobsecond = Thread(target=job2)
    jobfirst.start()
    jobsecond.start()



# sched = BlockingScheduler()
# # # Schedules job_function to be run from mon to fri
# sched.add_job(letsGetStarted, 'cron',  day_of_week='mon-fri', hour=7, minute=5)
# sched.start()
letsGetStarted()