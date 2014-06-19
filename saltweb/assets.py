#!/usr/bin/env python
#coding=utf-8
#author: hhr
import time,sys,os
import salt.client
import comm, db_connector
from saltweb.models import *
from django.core.mail import send_mail


code = os.system("/etc/init.d/salt-master status >/dev/null")
if code != 0: sys.exit()

saltids = [row['saltid'] for row in Hosts.objects.values('saltid')]
c = salt.client.LocalClient()
try:
    grains = c.cmd('*', 'grains.items')
except:
    sys.exit()
vmrets = c.cmd('*','cmd.run',['ls /dev/*vda'],timeout=5)    #xen是/dev/xvda，kvm是/dev/vda
for saltid,grain in grains.items():
    chage = {}
    os = grain['osfullname']+grain['osrelease']
    cpu = grain['cpu_model']
    hostname = grain['nodename']
    mem = grain['mem_total']
    cpunum = int(grain['num_cpus'])
    ip = [i for i in grain['ipv4'] if i.startswith(comm.network_list)][0]
    if saltid in saltids:
        ret = Hosts.objects.get(saltid=saltid)
        if ip != ret.ip:chage['ip']='%s > %s' % (ret.ip,ip) 
        if os != ret.os:chage['os']='%s > %s' % (ret.os,os) 
        if cpu != ret.cpu:chage['cpu']='%s > %s' % (ret.cpu,cpu)
        if cpunum != ret.cpunum:chage['cpunum']='%s > %s' % (ret.cpunum,cpunum)
        if mem != int(ret.mem):chage['mem']='%s > %s' % (ret.mem,mem)
        if hostname != ret.hostname:chage['hostname']='%s > %s' % (ret.hostname,hostname)
        if chage:
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Hosts.objects.filter(saltid=saltid).update(ip=ip,cpu=cpu,cpunum=cpunum,mem=mem,hostname=hostname,os=os,nowtime=nowtime)
            Chagelog.objects.create(saltid=saltid,ip=ip,chage=str(chage))
            subject=u'Hardware chage ' + saltid
            send_mail(subject,str(chage),comm.from_mail,comm.samail_list)
    else:
        ips = [row['ip'] for row in Hosts.objects.values('ip')]
        if ip in ips:
            Hosts.objects.filter(ip=ip).delete()
            Monitor.objects.filter(ip=ip).delete()
        Hosts.objects.create(saltid=saltid,cpu=cpu,cpunum=cpunum,mem=mem,hostname=hostname,os=os,ip=ip)
for saltid,vmret in vmrets.items():
    if 'No such file or directory' in vmret:
        chage = {}
        modelcmd = "dmidecode | grep 'Product Name: '|head -1|awk -F\: '{print $2}'|awk '{print $1,$2,$3}'"
        modelret = c.cmd(saltid,'cmd.run',[modelcmd],timeout=5)
        sncmd = "dmidecode -s system-serial-number"
        snret = c.cmd(saltid,'cmd.run',[sncmd],timeout=5)
        diskcmd = "fdisk -l 2>/dev/null|egrep '^Disk /dev/'|awk '{print $3,$4}'"
        diskret = c.cmd(saltid,'cmd.run',[diskcmd],timeout=5)
        ret = Hosts.objects.get(saltid=saltid) 
        if modelret[saltid] != ret.model:chage['model']='%s > %s' % (ret.model,modelret[saltid])
        if snret[saltid] != ret.sn:chage['sn']='%s > %s' % (ret.sn,snret[saltid])
        if diskret[saltid] != ret.disk:chage['disk']='%s > %s' % (ret.disk,diskret[saltid])
        if chage:
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Hosts.objects.filter(saltid=saltid).update(model=modelret[saltid],
                    sn=snret[saltid],disk=diskret[saltid],host_type='实体机',nowtime=nowtime)
            if ret.model != 'Null':
                ip = Hosts.objects.get(saltid=saltid).ip
                print ip
                Chagelog.objects.create(saltid=saltid,ip=ip,chage=str(chage))
                subject=u'Hardware chage ' + saltid
                send_mail(subject,str(chage),comm.from_mail,comm.samail_list)
