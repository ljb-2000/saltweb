#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time,re
import subprocess
import threading,multiprocessing
import comm, db_connector
from saltweb.models import *

def ping(ip,tgt):
    returncode = subprocess.call("ping -c 2 -w 3 "+ip,shell=True,stdout=open('/dev/null','w'),stderr=subprocess.STDOUT)
    if returncode != 0:
        ret = [tgt,ip,'Down']
    else:
        ret = [tgt,ip,'UP']
    return ret
if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=comm.thread_num)
    result = []
    results = Hosts.objects.values('ip','saltid')
    for ret in results:
        ip = ret['ip']
        tgt = ret['saltid']
        result.append(pool.apply_async(ping, (ip,tgt)))
    pool.close()
    rets = [i.get() for i in result]
    saltids = [r['saltid'] for r in Hosts.objects.values('saltid')]
    for i in rets:
        if i[0] in saltids:
            Hosts.objects.filter(saltid=i[0]).update(pingstatus=i[2])
        else:
            Hosts.objects.create(saltid=i[0],ip=i[1],pingstatus=i[2])
