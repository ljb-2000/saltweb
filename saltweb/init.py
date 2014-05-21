#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time,re
import threading
import comm
from saltweb.models import *

os.system('cd %s ;nohup python -m SimpleHTTPServer >/tmp/t.out 2>&1 &' % comm.upload_dir)
#Pro_type.objects.all().delete()
#Pro_type.objects.create(name='SSH')
#Pro_type.objects.create(name='SSH-KEY')
Monitortype.objects.all().delete()
Monitortype.objects.create(name='connum',alias='连接数')
Monitortype.objects.create(name='load',alias='负载')
os.system('python %smanage.py' % comm.script_dir )
os.system('python %shostping.py' % comm.script_dir)
os.system('python %smonitor.py' % comm.script_dir)
os.system('cd %s ;nohup python -m SimpleHTTPServer >/tmp/t.out 2>&1 &' % comm.upload_dir)
os.system('rm -rf %s %s' % (comm.rrd_dir,comm.rrdpic_dir))
os.system('uwsgi --ini %s' % comm.base_dir + 'uwsgi.ini')
if not os.path.exists(rrdfile):rrdcreate1(rrdfile,rrdstep)
os.system('echo "auto_accept: True" >>/etc/salt/master')
os.system('grep "^default_include: master.d/\*\.conf" /etc/salt/master >/dev/null 2>&1|| echo "default_include: master.d/*.conf" >> /etc/salt/master')
groupsconfdir = os.path.dirname(comm.groupsconf)
if not os.path.exists(groupsconfdir): os.makedirs(groupsconfdir)
if not os.path.exists(comm.groupsconf): os.system('echo "nodegroups:\n    dfgroup: testhostid" > %s' % comm.groupsconf)
