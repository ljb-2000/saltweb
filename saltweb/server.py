#!/usr/bin/env python
#coding=utf-8
#author: hhr
import time
import salt
import comm, db_connector
from saltweb.models import *

saltids = [row['saltid'] for row in Monitor.objects.values('saltid')]
c = salt.client.LocalClient()
grains = c.cmd('*', 'grains.items')
#loadcmd = "cat /proc/loadavg |awk '{print $1}'"
loadcmd = "cat /proc/loadavg |awk '{print $1}'"
loadret = c.cmd('*','cmd.run',[loadcmd],timeout=5)
connumcmd = "netstat -n|awk '/^tcp/ {++S[$NF]} END {for (a in S) print a,S[a]}'"
connumret = c.cmd('*','cmd.run',[connumcmd],timeout=5)
for saltid,load in loadret.items():
    if saltid in saltids:
	    Monitor.objects.filter(saltid=saltid).update(load=load)
    #else:
	#    Monitor.objects.create(saltid=saltid,load=load)
for saltid,connum in connumret.items():
    if saltid in saltids:
        Monitor.objects.filter(saltid=saltid).update(connum=connum)
    #else:
    #    Monitor.objects.create(saltid=saltid,connum=connum)
