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
    nowtime = time.strftime("%Y-%m-%d %X")
    status = r[1]
    if str(status) != '200':
        num = Url.objects.filter(proname=proname)[0].num
        num +=1
        lasttime = Url.objects.filter(proname=proname)[0].lasttime
        if not lasttime and num >3:
            num = 0
            sendmail = 1
            lasttime = time.strftime("%Y-%m-%d %X")
            Url.objects.filter(proname=proname).update(num=num,nowtime=nowtime,sendmail=sendmail,lasttime=lasttime)
        if num > 3 and int(time.mktime(time.strptime(nowtime, '%Y-%m-%d %X'))) > int(time.mktime(time.strptime(lasttime, '%Y-%m-%d %X'))) + comm.interval:
            num = 0
            sendmail = 1
            lasttime = time.strftime("%Y-%m-%d %X")
            Url.objects.filter(proname=proname).update(num=num,nowtime=nowtime,sendmail=sendmail,lasttime=lasttime)
        Url.objects.filter(proname=proname).update(status=str(status),num=num,nowtime=nowtime)
    else:
        Url.objects.filter(proname=proname).update(status=str(status),num=0,nowtime=nowtime)
errs = [i.proname for i in Url.objects.filter(sendmail=1,closemail=0)]
if errs:
    for err in errs:
        maillist = Url.objects.filter(proname=err)[0].contact.split(',')
        maillist.extend(comm.samail_list)
        status = Url.objects.filter(proname=err)[0].status
        msg = u'CRITICAL: url monitor fail %s status %s' % (err,status)
        print msg
        send_mail(msg,"",comm.from_mail,comm.samail_list)
        Alarm.objects.create(hostid=str(errs),msg=msg,to=maillist)
        users = [row['username'] for row in User.objects.values('username')]
        for user in users:
            Msg.objects.create(msgfrom='systemmonitor',msgto=user,title=msg,content="")
        Url.objects.filter(proname=err).update(sendmail=0)
