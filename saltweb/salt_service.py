#!/usr/bin/env python
import os,sys,time
import comm

def service(servicename,cmd):
    if service_status(servicename) == 'Running':
        print "\033[33;1m%s service is already running!\033[0m" % servicename
    else:
        if os.system(cmd) == 0:
            print '\033[32;1m%s server start success!\n\033[0m' % servicename
        else:
            print '\033[31;1m%s server start failed!\n\033[0m' % servicename

def stop_service(service_name):
    cmd = "ps -ef| grep %s|grep -v restart|grep -v grep|awk '{print $2}'|xargs kill -9" %(service_name)    
    if service_status(service_name) == 'Running':
        cmd_result = os.system(cmd)
        if cmd_result == 0:
            print '..............\n'
            time.sleep(1)
            print '\033[31;1m%s stopped! \033[0m' % service_name
        else:
            print '\033[31;1mCannot stop %s service successfully,please manually kill the pid!\033[0m' % service_name
    else:
        print 'Service is not running...,nothing to kill! '

def service_status(service_name):
    cmd = "ps -ef |grep %s|grep -v restart|grep -v grep |awk '{print $2}'" % service_name 
    result = os.popen(cmd).read().strip()
    try:
        service_pid = result.split()[0]
        if service_pid:
            print "\033[32;1m%s monitor service is running...\033[0m" % service_name
            return "Running"
    except IndexError:
        print "\033[31;1m%s service is not running....\033[0m" % service_name
        return "Dead"

uwsgicmd = 'uwsgi --ini %suwsgi.ini' % comm.base_dir
#minioncmd = '/etc/init.d/salt-minion start'
mastercmd = '/etc/init.d/salt-master start'
phpfpmcmd = '/etc/init.d/php-fpm start'
nginxcmd = '/etc/init.d/nginx start'
saltcroncmd = 'python %ssaltcron.py &' % comm.script_dir
SimpleHTTPServercmd = 'cd %s ;nohup python -m SimpleHTTPServer >/tmp/t.out 2>&1 &' % comm.upload_dir
#services = {'uwsgi':uwsgicmd,'salt-master':mastercmd,'salt-minion':minioncmd,'php-fpm':phpfpmcmd,'nginx':nginxcmd,'saltcron':saltcroncmd}
services = {'uwsgi':uwsgicmd,'salt-master':mastercmd,'php-fpm':phpfpmcmd,'nginx':nginxcmd,'saltcron':saltcroncmd,'SimpleHTTPServer':SimpleHTTPServercmd}
try:
    if sys.argv[1].startswith('restart') and sys.argv[1] != 'restart':
        servicename = sys.argv[1].replace('restart','')
        print sys.argv[1]
        print servicename
        if servicename in services.keys():
            stop_service(servicename)
            service(servicename,services[servicename])
            sys.exit(0)
    if sys.argv[1] == 'start':
        for servicename,startcmd in services.items():
            service(servicename,startcmd)
    elif sys.argv[1] == 'stop':
        for servicename in services:
            stop_service(servicename)
    elif sys.argv[1] == 'status':
        for servicename in services:
            service_status(servicename)
    elif sys.argv[1] == 'restart':
        for servicename,startcmd in services.items():
            stop_service(servicename)
            service(servicename,startcmd)            
    else:
        print "Use: stop|start|restart|etatus|restartuwsgi"
except IndexError:
    print 'No argument detected!\nUse: stop|start|restart|status'

