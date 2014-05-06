#!/usr/bin/env python
#coding=utf-8
#author: hhr
import salt
import sys,time,os
import comm, db_connector
from django.core.mail import send_mail
from saltweb.models import *


rets = Url.objects.all()
for ret in rets:
    proname = ret.proname
    urlname = ret.urlname
    ip = ret.ip
    port = ret.port
    r = comm.curl(urlname,ip,port)
    pubtime = time.strftime("%Y-%m-%d %H:%M:%S")
    Url.objects.filter(urlname=urlname,ip=ip,port=port).update(domainname=r[0],state=r[1],pubtime=pubtime)
