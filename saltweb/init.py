#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time,re
import threading
import comm, db_connector
from saltweb.models import *

Monitortype.objects.all().delete()
Monitortype.objects.create(name='connum',alias='连接数')
Monitortype.objects.create(name='load',alias='负载')
Mastermonitor.objects.all().delete()
Mastermonitor.objects.create(ip='%s' % comm.masterip)
os.system('rm -rf %s/* %s' % (comm.rrd_dir,comm.rrdpic_dir))
