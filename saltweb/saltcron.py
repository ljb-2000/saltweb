#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time
import comm

from apscheduler.scheduler import Scheduler
sched = Scheduler(daemonic = False)
def job_function(server):
    os.system('python %s.py' % server)
sched.add_interval_job(job_function,hours=1,args=['manage'])
sched.add_interval_job(job_function,seconds=60,args=['hostping'])
sched.add_interval_job(job_function,minutes=2,args=['monitor'])
#sched.add_interval_job(job_function,minutes=1,args=['server'])
#sched.add_interval_job(job_function,seconds=120,args=['rrdupdate'])
sched.add_interval_job(job_function,minutes=5,args=['urlmonitor'])
time.sleep(2)
sched.start()

