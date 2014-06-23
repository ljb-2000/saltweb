#!/usr/bin/env python
#coding=utf-8
#author: hhr
####################
#全局常量
from_mail = 'saltweb@hhr.com'
samail_list = ['hhr66@qq.com',]
interval = 7200 #报警间隔
masterip = '172.16.1.237'
network_list = ('172.16','192.168','10.0')
pagelimit = 8	#分页
dangercmdlist = ('rm','reboot','init ','shutdown')
download_url = 'http://%s:8000/' % masterip
base_dir = '/root/saltweb/'
script_dir = '%ssaltweb/' % base_dir
upload_dir = '%supload/' % base_dir
sshdefaultport = 50718
thread_num = 20
rrdstep = 120 
groupsconf = '/etc/salt/group.conf'
dbname = 'saltweb'
dbuser = 'root'
dbpasswd = '123'
####################
def ssh(ip,port,user,passwd,cmd):
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip,int(port),user,passwd,timeout=5)
    except:
        return {ip:"Error: connect fail !!!"}
    try:
        stdin, stdout, stderr = ssh.exec_command("export LANG=en_US.UTF-8 ; %s" % cmd)
    except:
        return {ip:"Error: exec fail !!!"}
    i = stderr.readlines()
    if i:
        return {ip:''.join(i)}
    return {ip:''.join(stdout.readlines())}
    ssh.close()

def rrdcreate1(rrdfile,rrdstep):
    import os,rrdtool
    hb = rrdstep*2
    rrdpath = os.path.dirname(rrdfile)
    if not os.path.isdir(rrdpath):
        os.makedirs(rrdpath)
    rrdb=rrdtool.create(str(rrdfile),'--step',str(rrdstep),
        'DS:ds1:GAUGE:%d:U:U' % hb,
        'RRA:LAST:0.5:1:600',
        'RRA:AVERAGE:0.5:5:600',
        'RRA:MAX:0.5:5:600',
        'RRA:MIN:0.5:5:600')
def rrdcreate2(rrdfile,rrdstep):
    import os,rrdtool
    hb = rrdstep*2
    rrdpath = os.path.dirname(rrdfile)
    if not os.path.isdir(rrdpath):
        os.makedirs(rrdpath)
    rrdb=rrdtool.create(rrdfile,'--step',str(rrdstep),
        'DS:ds1:GAUGE:%d:U:U' % hb,
        'DS:ds2:GAUGE:%d:U:U' % hb,
        'RRA:LAST:0.5:1:600',
        'RRA:AVERAGE:0.5:5:600',
        'RRA:MAX:0.5:5:600',
        'RRA:MIN:0.5:5:600')

#创建rrd文件时统一定义DS名为ds1
def rrdgraph1(pic,rrdfile,start,title,data1,vertical):
    import time,rrdtool
    now=time.strftime('%Y-%m-%d %H\:%M\:%S')
    rrdtool.graph(str(pic),'--start',str(start),
        '--title',str(title),
        '--vertical-label',str(vertical),
        #'--font','TITLE:10:/usr/share/fonts/dejavu/msyh.ttf',
        'DEF:ds1=%s:ds1:LAST' % str(rrdfile),
        'LINE1:ds1#0000FF:%s' % data1,
        'GPRINT:ds1:LAST:Current\:%2.0lf',
        'GPRINT:ds1:AVERAGE:AVERAGE\:%2.0lf',
        'GPRINT:ds1:MAX:MAX\:%2.0lf\\n',
        'COMMENT:update time %s\\r' % str(now),)

#创建rrd文件时统一定义DS名为ds1和ds2
def rrdgraph2(pic,rrdfile,start,title,data1,data2,vertical):
    import time,rrdtool
    now=time.strftime('%Y-%m-%d %H\:%M\:%S')
    rrdtool.graph(pic,'--start',start,
        '--title',title,
        '--vertical-label',vertical,
        #'--font','TITLE:10:/usr/share/fonts/dejavu/msyh.ttf',
        'DEF:ds1=%s:ds1:LAST' % rrdfile,
        'DEF:ds2=%s:ds2:LAST' % rrdfile,
        'LINE1:ds1#0000FF:%s' % data1,
        'GPRINT:ds1:LAST:Current\:%2.0lf',
        'GPRINT:ds1:AVERAGE:AVERAGE\:%2.0lf',
        'GPRINT:ds1:MAX:MAX\:%2.0lf\\n',
        'LINE1:ds2#00FF00:%s' % data2,
        'GPRINT:ds2:LAST:Current\:%2.0lf',
        'GPRINT:ds2:AVERAGE:AVERAGE\:%2.0lf',
        'GPRINT:ds2:MAX:MAX\:%2.0lf\\n',
        'COMMENT:update time %s\\r' % now,)

def curl(url,ip,port):
    import os
    from urlparse import urlparse
    ipport = str(ip) + ':' + str(port)
    output = urlparse(url)
    newurl = output[0]+"://"+ipport+output[2]
    domainname = output[1].split(':')[0]
    ret = os.popen("curl --connect-timeout 3 -s -I -H 'Host: %s' '%s'|head -1|awk '{print $2}'" %(domainname,newurl) ).read().strip('\n')
    if not ret: ret = "down"
    return [domainname,ret]

def cmdminion(host):
    cmd = "Sys_ver=`uname -a|awk -F'el' '{print substr($2,1,1)}'`;"
    cmd += "rpm -q epel-release >/dev/null;"
    cmd += "num=$?;"
    cmd += '[ $num -ne 0 ] && [ $Sys_ver -eq 5 ] && sudo rpm -Uvh http://mirrors.sohu.com/fedora-epel/5/x86_64/epel-release-5-4.noarch.rpm >/dev/null 2>&1;'
    cmd += '[ $num -ne 0 ] && [ $Sys_ver -eq 6 ] && sudo rpm -Uvh http://mirrors.sohu.com/fedora-epel/6/x86_64/epel-release-6-8.noarch.rpm >/dev/null 2>&1;'
    cmd += 'rpm -q salt-minion >/dev/null || sudo yum -y install salt-minion >/dev/null 2>&1'
    cmd += '&& sudo sed -i "$ a\master: %s" /etc/salt/minion ' % masterip
    cmd += '&& sudo sed -i "$ a\id: %s_`hostname`" /etc/salt/minion ' % host
    cmd += '&& sudo rm -f /etc/salt/pki/minion/minion_master.pub'
    cmd += '&& sudo /etc/init.d/salt-minion restart >/dev/null'
    cmd += '&& echo "Success %s_`hostname`"' % host
    return cmd
