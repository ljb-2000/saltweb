#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time,re
import threading
import comm, db_connector
from saltweb.models import *

os.system('salt-key -D -y')
Hosts.objects.all().delete()
Monitor.objects.all().delete()
Alarm.objects.all().delete()
Chagelog.objects.all().delete()
Deploylog.objects.all().delete()
Group.objects.all().delete()
Log.objects.all().delete()
Minions.objects.all().delete()
Mastermonitor.objects.all().delete()
Msg.objects.all().delete()
Todo.objects.all().delete()
Upload.objects.all().delete()
Url.objects.all().delete()
Users.objects.all().delete()
