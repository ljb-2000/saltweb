#!/usr/bin/env python
#coding=utf-8
#author: hhr
#salt-master、salt-minion宕机邮件报警
#添加新minion或删除minion自动更新数据库

import salt
import sys, time ,os
import comm, db_connector
from django.core.mail import send_mail
from saltweb.models import *

#判断master状态
if not Mastermonitor.objects.filter(id=1):
    Mastermonitor.objects.create(ip='%s' % comm.masterip)
code = os.system("/etc/init.d/salt-master status >/dev/null")
if code != 0:
    status = 'down'
    Mastermonitor.objects.filter(id=1).update(status=status)
    nowtime = time.strftime("%Y-%m-%d %X")
    lasttime = Mastermonitor.objects.filter(id=1)[0].lasttime
    if not lasttime or int(time.mktime(time.strptime(nowtime, '%Y-%m-%d %X'))) > int(time.mktime(time.strptime(lasttime, '%Y-%m-%d %X'))) + comm.interval:
        Mastermonitor.objects.filter(id=1).update(nowtime=nowtime,lasttime=nowtime)
        send_mail(u'CRITICAL: salt-master down',u'saltwebmaster',comm.from_mail,comm.samail_list)
        Alarm.objects.create(hostid="saltwebmaster",msg='CRITICAL: salt-master down',to=comm.samail_list)
    sys.exit()
else:
    status = 'up'
    Mastermonitor.objects.filter(id=1).update(status=status)

#minion状态
c = salt.client.LocalClient()
rets = c.cmd('*','test.ping')
saltids = [r['saltid'] for r in Hosts.objects.values('saltid')]
saltkeys = c.run_job('*','cmd.run',['echo'])['minions']
newlist = list(set(saltkeys).difference(set(saltids)))   #新增minion列表
oldlist = list(set(saltids).difference(set(saltkeys)))  #删除minion列表
downlist = list(set(saltids).difference(set(rets.keys())))  #宕机列表
if newlist:
    for saltid in newlist:
        ip = saltid.split('_')[0]
        Hosts.objects.create(saltid=saltid,ip=ip,saltstatus='False') 
    saltids = [r['saltid'] for r in Hosts.objects.values('saltid')]
if oldlist:
    for saltid in oldlist:
        Hosts.objects.filter(saltid=saltid).delete()
    saltids = [r['saltid'] for r in Hosts.objects.values('saltid')] 
for down in downlist:
    rets[down] =  'False'
for saltid,saltstatus in rets.items():
    if saltid in saltids:
        num = 0
        nowtime = time.strftime("%Y-%m-%d %X")
        Hosts.objects.filter(saltid=saltid).update(saltstatus=str(saltstatus),nowtime=nowtime)
        if str(saltstatus) == 'False':
            num = Hosts.objects.filter(saltid=saltid)[0].num
            num +=1
            lasttime = Hosts.objects.filter(saltid=saltid)[0].lasttime
            if not lasttime and num >3:
                num = 0
                sendmail = 1
                lasttime = time.strftime("%Y-%m-%d %X")
                Hosts.objects.filter(saltid=saltid).update(num=num,nowtime=nowtime,lasttime=lasttime,sendmail=sendmail)
            if num > 3 and int(time.mktime(time.strptime(nowtime, '%Y-%m-%d %X'))) > int(time.mktime(time.strptime(lasttime, '%Y-%m-%d %X'))) + comm.interval:
                num = 0
                sendmail = 1
                lasttime = time.strftime("%Y-%m-%d %X")
                Hosts.objects.filter(saltid=saltid).update(num=num,nowtime=nowtime,lasttime=lasttime,sendmail=sendmail)
            Hosts.objects.filter(saltid=saltid).update(num=num,nowtime=nowtime)
        else:
            Hosts.objects.filter(saltid=saltid).update(num=num)
downhostlist = [i.saltid for i in Hosts.objects.filter(sendmail=1,closemail=0)]
if downhostlist:
    Hosts.objects.all().update(sendmail=0)
    msg = u'CRITICAL: host saltstatus down'
    send_mail(msg,str(downhostlist),comm.from_mail,comm.samail_list)
    Alarm.objects.create(hostid=str(downhostlist),msg=msg,to=comm.samail_list)
    users = [row['username'] for row in User.objects.values('username')]
    for user in users:
        Msg.objects.create(msgfrom='systemmonitor',msgto=user,title=msg,content=str(downhostlist))
