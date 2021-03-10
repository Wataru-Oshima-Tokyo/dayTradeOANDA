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
    if(targetTime <10):
        current_time = 'h0' + str(targetTime)
    else:
        current_time = 'h' + str(targetTime)
    return current_time

def job2():
    japanTime = datetime.datetime.now()
    newyorkTime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    londonTime = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
    todays_date = int(japanTime.strftime("%Y%m%d")) 
    finishTime = 0; 
    flag = False
    if(todays_date >20210314 and todays_date < 20211107):
        endTime = 6
    else:
        endTime = 7
    while (finishTime != endTime):
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

def hello():
    print(" this works!")


sched = BlockingScheduler()
# # Schedules job_function to be run from mon to fri
now = datetime.datetime.now()
startTime = int(now.strftime("%m%d"))
# if(startTime > 314 and startTime<1107):
#     hour =6
# else:
#     hour =7
sched.add_job(letsGetStarted, 'cron',  day_of_week='mon-fri', hour='0-23', minute='0-59')
sched.start()
