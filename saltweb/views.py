#!/usr/bin/env python
#coding=utf-8
#author: hhr
import time,os
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.decorators import login_required 
from django.core.cache import cache
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.contrib.auth.models import User
from django.template import RequestContext
import multiprocessing, threading
import salt
import base64
import csv
from saltweb.models import *
from saltweb.form import *
from saltweb.comm import *
import db_connector

def index(request):
    if str(request.user) != "AnonymousUser":
        user = request.user
        msgnum = Msg.objects.filter(isread=0,msgto=user).count()
        return render_to_response('index.html',locals())
    else:
        return HttpResponseRedirect('/salt/login/')

def account_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = request.user
    login_err = "对不起，用户名或密码不对！"
    user = auth.authenticate(username=username,password=password)
    if user is not None:
        auth.login(request,user)
        return HttpResponseRedirect('/salt/')
    else:
        return render_to_response('login.html',locals())

def login(request):
    user = request.user
    return render_to_response('login.html',locals())

def logout(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    auth.logout(request)
    return HttpResponseRedirect('/salt/login/')

@login_required
def monitor(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    up = Monitor.objects.filter(saltstats='True').count()
    down = Monitor.objects.filter(saltstats='False').count()
    total = Monitor.objects.count() 
    ONE_PAGE_OF_DATA = pagelimit
    curPage = int(request.GET.get('curPage', '1'))
    allPage = int(request.GET.get('allPage','1'))
    pageType = str(request.GET.get('pageType', ''))
    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1
    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    posts = Monitor.objects.order_by("saltstats")[startPos:endPos]
    if curPage == 1 and allPage == 1: 
        allPostCounts = Monitor.objects.count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
                allPage += 1
    id = request.GET.get('id',)
    closemail = request.GET.get('closemail',)
    Monitor.objects.filter(id=id).update(closemail=closemail)
    return render_to_response('monitor.html',locals())

@login_required
def monitor1(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    saltids = [row['saltid'] for row in Hosts.objects.values('saltid')]
    typerets = Monitortype.objects.all()
    monitortypes = [row['name'] for row in Monitortype.objects.values('name')]
    host = ''
    start = ''
    times = ''
    if request.method == 'POST':
        host = request.POST.get('host',)
        type = request.POST.get('type',)
        times = request.POST.get('time',)
        if request.POST.has_key("rrdcreate"):
            rrdfile = rrd_dir + host + '/'+ type + '.rrd'
            if not os.path.exists(rrdfile):
                rrdcreate1(rrdfile,rrdstep)
        if request.POST.has_key("rrddel"):
            rrdpic = rrdpic_dir + host + '/' + type + '.png'
            rrdfile = rrd_dir + host + '/'+ type + '.rrd'
            if os.path.exists(rrdfile):
                os.remove(rrdfile)
            if os.path.exists(rrdpic):
                os.remove(rrdpic)
        if not os.path.isdir(rrdpic_dir + host):
            os.makedirs(rrdpic_dir + host)
        if not os.path.isdir(rrd_dir + host):
            os.makedirs(rrd_dir + host)
        #if not host: host = localhostid
        start = 'N-%s' % times
        rrdfilelist = os.listdir(rrd_dir + host)
        for i in rrdfilelist:
            type = os.path.splitext(i)[0]
            rrdfile1 = rrd_dir + host + '/' + i
            pic1 = rrdpic_dir + host + '/' + type + '.png'
            if not times:start = 'N-3600'
            title1 = host + ' ' + type
            data1 = str(type)
            vertical = ''
            rrdgraph1(pic1,rrdfile1,start,title1,data1,vertical)
        graphlist = os.listdir(rrdpic_dir + host)
    return render_to_response('monitor1.html',locals())

@login_required
def alarm(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    rets = Alarm.objects.order_by('-id')
    return render_to_response('alarm.html',locals())

@login_required
def server(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    posts = []
    if request.method == 'POST':
        saltid = request.POST.get('saltid',)
        type = request.POST.get('type',)
        c = salt.client.LocalClient()
        minions = c.run_job(saltid,'cmd.run',['echo'],expr_form=type)['minions']
        for saltid in minions:
            posts.append(Monitor.objects.filter(saltid=saltid))
    return render_to_response('server.html',locals())

@login_required
def assets(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    saltids = [row['saltid'] for row in Hosts.objects.values('saltid')]
    ONE_PAGE_OF_DATA = pagelimit
    saltid = request.POST.get('host','')
    if request.method == 'POST' and saltid != 'all':
        allPostCounts = 1
        curPage = 1
        allPage = 1
        pageType = ''
        posts = Hosts.objects.filter(saltid=saltid)
    else:
        curPage = int(request.GET.get('curPage', '1'))
        allPage = int(request.GET.get('allPage','1'))
        pageType = str(request.GET.get('pageType', ''))
        if pageType == 'pageDown':
            curPage += 1
        elif pageType == 'pageUp':
            curPage -= 1

        startPos = (curPage - 1) * ONE_PAGE_OF_DATA
        endPos = startPos + ONE_PAGE_OF_DATA
        posts = Hosts.objects.order_by("-update_date")[startPos:endPos]
        if curPage == 1 and allPage == 1: 
            allPostCounts = Hosts.objects.count()
            allPage = allPostCounts / ONE_PAGE_OF_DATA
            remainPost = allPostCounts % ONE_PAGE_OF_DATA
            if remainPost > 0:
                    allPage += 1
    return render_to_response('assets.html',locals())

@login_required
def minions(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    saltids = [row['saltid'] for row in Hosts.objects.values('saltid')]
    if request.method == 'POST':
        if request.POST.has_key("add"):
            port = sshdefaultport
            host = request.POST.get('host','')
            username = request.POST.get('username','')
            passwd = request.POST.get('passwd','')
            cmd = "Sys_ver=`uname -a|awk -F'el' '{print substr($2,1,1)}'` "
            cmd += '; [ $Sys_ver -eq 5 ] && sudo rpm -Uvh http://mirrors.sohu.com/fedora-epel/5/x86_64/epel-release-5-4.noarch.rpm \
                >/dev/null 2>&1'
            cmd += '; [ $Sys_ver -eq 6 ] && sudo rpm -Uvh http://mirrors.sohu.com/fedora-epel/6/x86_64/epel-release-6-8.noarch.rpm \
                >/dev/null 2>&1'
            cmd += '; sudo yum -y install salt-minion >/dev/null'
            cmd += '&& sudo sed -i "$ a\master: %s" /etc/salt/minion ' %masterip
            cmd += '&& sudo sed -i "$ a\id: %s_`hostname`" /etc/salt/minion ' % host
            cmd += '&& sudo /etc/init.d/salt-minion restart >/dev/null'
            cmd += "&& echo 'Success'"
            def sshfc():
                Monionslog.objects.create(name='add_minion',ip=host)
                id = Monionslog.objects.order_by('-id')[0].id
                ret = ssh(host,port,username,passwd,cmd)
                endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                Monionslog.objects.filter(id=id).update(status='已完成',deployret=ret[host],endtime=endtime)
            threading.Thread(target=sshfc).start()
            time.sleep(1)   
        if request.POST.has_key("del"):
            saltid = request.POST.get('saltid','') 
            Monionslog.objects.create(name='del_minion',saltid=saltid)
            id = Monionslog.objects.order_by('-id')[0].id
            cmd = 'sed -i "s/^master/#master/g" /etc/salt/minion'
            cmd += '&& /etc/init.d/salt-minion stop >/dev/null'
            cmd += "&& echo 'Success'"
            c = salt.client.LocalClient()
            ret = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
            if ret:
                ret = 'Success'
            else:
                ret = 'Error: minion 宕机或者salt-minion服务未开启'
            os.system('salt-key -d %s -y' % saltid )
            Hosts.objects.filter(saltid=saltid).delete()
            Monitor.objects.filter(saltid=saltid).delete()
            endtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Monionslog.objects.filter(id=id).update(status='已完成',deployret=ret,endtime=endtime)
            Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='del_minion',execerr=ret)
    deployrets = Monionslog.objects.order_by('-id')[0:7]
    return render_to_response('minions.html',locals())

@login_required
def urlmonitor(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        if request.POST.has_key("add"):
            proname = request.POST.get('proname','')
            urlname = request.POST.get('urlname','')
            ip = request.POST.get('ip','')
            port = request.POST.get('port','')
            r = curl(urlname,ip,port)
            proname = proname + '-' + ip
            if not Url.objects.filter(proname=proname) and urlname.startswith('http://'):
                Url.objects.create(proname=proname,ip=ip,port=port,urlname=urlname,domainname=r[0],state=r[1])
            else: 
                msg = '工程名已存在或者url地址不是以http开头'
        if request.POST.has_key("search"):
            re = request.POST.get('searchproname','')
            if re:
                pronames = [row['proname'] for row in Url.objects.values('proname')]
                rets = [Url.objects.get(proname=i) for i in pronames if re in i]
                return render_to_response('urlmonitor.html',locals())
        if request.POST.has_key("updateall"):
           os.popen('python %ssaltweb/urlmonitor.py' % base_dir) 
    rets = Url.objects.order_by("-state")
    return render_to_response('urlmonitor.html',locals())

def urlupdate(request,id=''):
    ret = Url.objects.get(id=id)
    urlname = ret.urlname
    ip = ret.ip
    port = ret.port
    r = curl(urlname,ip,port)
    pubtime = time.strftime("%Y-%m-%d %H:%M:%S")
    Url.objects.filter(id=id).update(domainname=r[0],state=r[1],pubtime=pubtime)
    return HttpResponseRedirect('/salt/urlmonitor/')    

def urldel(request,id=''):
    Url.objects.filter(id=id).delete()
    return HttpResponseRedirect('/salt/urlmonitor/')

@login_required
def chagelog(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    rets = Chagelog.objects.order_by("-updatetime")
    return render_to_response('chagelog.html',locals())

@login_required
def saltcmd(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    dangercmd = ",".join(dangercmdlist)
    if request.method == 'POST':	
    	c = salt.client.LocalClient()
        saltid = request.POST.get('saltid','')
        fun = request.POST.get('fun','')
        cmd = request.POST.get('cmd','')
        type = request.POST.get('type','')
        minions = c.run_job(saltid,'cmd.run',['echo'],expr_form=type)['minions']
        print minions
        dangercmds = [i for i in dangercmdlist if i in cmd]
	if not dangercmds:
            ret1 = c.cmd(saltid,fun,[cmd],expr_form=type,timeout=99)
            execerr = list(set(minions).difference(set(ret1.keys())))
            total = len(minions)
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
	Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype=fun,cmd=cmd,execerr=execerr,logret=ret1)
    return render_to_response('saltcmd.html',locals())

@login_required
def sshcmd(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    dangercmd = ",".join(dangercmdlist)
    ips = [row['ip'] for row in Hosts.objects.values('ip')]
    users = [row.username for row in Users.objects.all()]
    ip = ''
    cmd = ''
    ret1 = {}
    if request.method == 'POST':
        host = request.POST.get('host','')
        if host == 'all':
            pool = multiprocessing.Pool(processes=thread_num)
            result = []
            for ip in ips:
                port = Hosts.objects.get(ip=ip).port
                username = request.POST.get('username','')
                passwd = Users.objects.get(username=username).passwd
                cmd = request.POST.get('cmd','')
                result.append(pool.apply_async(ssh, (ip,int(port),username,passwd,cmd)))
            pool.close()
            ret1 = [i.get() for i in result]
            total = len(ret1)
            execerr = [','.join(i.keys()) for i in ret1 if ','.join(i.values()).startswith('Error:')]
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
            Log.objects.create(user=str(user),ip=host,saltid='-',logtype='ssh',cmd=cmd,execerr=execerr,logret=ret1)
        elif host.startswith(network_list):
            port = Hosts.objects.get(ip=host).port
            username = request.POST.get('username','')
            passwd = Users.objects.get(username=username).passwd
            cmd = request.POST.get('cmd','')
            ret1 = [ssh(host,int(port),username,passwd,cmd)]
            execerr = [','.join(i.keys()) for i in ret1 if ','.join(i.values()).startswith('Error:')]
            errnum = len(execerr)
            execerr = 'total:1 errnum:%d errret:%s' % (errnum,','.join(execerr))
            Log.objects.create(user=str(user),ip=host,saltid='-',logtype='ssh',cmd=cmd,execerr=execerr,logret=ret1)
    return render_to_response('cmd.html',locals())

@login_required
def upload(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        upform = upfileForm(request.POST,request.FILES)
	downform = downfileForm(request.POST)
        if upform.is_valid():
            if upform.cleaned_data['file'].size > 5000000:
                ret = "File size no larger than 5M ,Upload Fail !!!"
            else:
                #print upform.cleaned_data['file'].size
                fp = file(upload_dir + upform.cleaned_data['file'].name,'wb')
                for chunk in upform.cleaned_data['file'].chunks():
                    fp.write(chunk)
                fp.close()
                ret = "Upload Success !!!"
	if downform.is_valid():
	    filename = downform.cleaned_data['file'].strip()
	    File = upload_dir + filename
            f = open(File)
	    data = f.read()
	    f.close()
	    response = HttpResponse(data,mimetype='application/octet-stream') 
	    response['Content-Disposition'] = 'attachment; filename=%s' % filename
	    return response
    else:
        ret = ''
	upform = upfileForm()
	downform = downfileForm()
    uploaddir = upload_dir
    files = os.listdir(upload_dir)
    return render_to_response('upload.html', locals())

@login_required
def audit(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        if request.POST.has_key("new"):
            name = request.POST.get('name','')
            if os.path.isfile(upload_dir + name):
                f = open(upload_dir + name)
                data = f.read()
                f.close()
            else:
                msg = "文件不存在!!!"
        if request.POST.has_key("audit"):
            name = request.POST.get('name','')
            if os.path.isfile(upload_dir + name):
                data = request.POST.get('data','')
                fp = file(upload_dir + name,'wb')
                fp.write(data)
                data = ''
                name = ''
                fp.close()
                msg = "修改成功!!!"
            else:
                msg = "文件不存在!!!"
            Log.objects.create(user=str(user),ip='localhost',saltid='-',logtype='auditfile',cmd=name,execerr=msg,logret='')
    uploaddir = upload_dir
    files = os.listdir(upload_dir)
    return render_to_response('audit.html', locals())

@login_required
def Syncfile(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    files = [file for file in os.listdir(upload_dir) if os.path.isfile("%s/%s" % (upload_dir,file))]
    if request.method == 'POST':
        filename = request.POST.get('filename','')
        local = upload_dir + filename
        remote = request.POST.get('path','')
        saltid = request.POST.get('saltid','')
        cmd = 'wget %s%s -O %s >/dev/null 2>&1 && echo "Syncfile Success !!!"' % (download_url,filename,remote)
        c = salt.client.LocalClient()
        rets = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
        minions = c.run_job(saltid,'cmd.run',['echo'])['minions']
        retok = [ret[0] for ret in rets.items() if "Success" in ret[1]]
        execerr = list(set(minions).difference(set(retok)))
        total = len(minions)
        errnum = len(execerr)
        execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
        Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='putfile',cmd=cmd,execerr=execerr,logret=rets)
    return render_to_response('syncfile.html', locals())

@login_required
def sysuser(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    users = [row.username for row in Users.objects.all()]
    if request.method == 'POST':
        if request.POST.has_key("adduser"):
            saltid = request.POST.get('saltid','')
            username = request.POST.get('username','')
            passwd = request.POST.get('passwd','')
            passwd1 = request.POST.get('passwd1','')
            usertype = request.POST.get('usertype','')
            if passwd == passwd1:
                cmd = "useradd %s >/dev/null 2>&1 &&echo %s|passwd --stdin %s >/dev/null 2>&1 &&echo 'successfully'" % (username,passwd,username)
                if usertype == '2':
                    cmd = '%s &&chattr -i /etc/sudoers && echo "%s  ALL=(ALL)  NOPASSWD: ALL">>/etc/sudoers && chattr +i /etc/sudoers' % (cmd,username)
                c = salt.client.LocalClient()
                minions = c.run_job(saltid,'cmd.run',['echo'])['minions']
                ret1 = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
                retok = [ret[0] for ret in ret1.items() if "successfully" in ret[1]]
                execerr = list(set(minions).difference(set(retok)))
                total = len(minions)
                errnum = len(execerr)
                execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
                if username in users:
                    Users.objects.filter(username=username).update(passwd=passwd)
                else:
                    Users.objects.create(username=username,passwd=passwd)
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='adduser',cmd=cmd,execerr=execerr,logret=ret1)
            else:
                ret1 = {"two passwd do not match!!!":''}
        if request.POST.has_key("deluser"):
            saltid = request.POST.get('saltid','')
            username = request.POST.get('username','') 
            c = salt.client.LocalClient()
            minions = c.run_job(saltid,'cmd.run',['echo'])['minions'] 
            cmd = "userdel %s >/dev/null 2>&1 &&echo 'successfully'" % username
            ret1 = c.cmd(saltid,'cmd.run',[cmd],timeout=5)      
            print ret1    
            retok = [ret[0] for ret in ret1.items() if "successfully" in ret[1]]
            execerr = list(set(minions).difference(set(retok)))
            total = len(minions)
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
            if username in users:
                Users.objects.filter(username=username).delete()
            Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='deluser',cmd=cmd,execerr=execerr,logret=ret1)
        if request.POST.has_key("chpasswd"):
            saltid = request.POST.get('saltid','')
            username = request.POST.get('username','')
            passwd = request.POST.get('passwd','')
            passwd1 = request.POST.get('passwd1','')
            cmd = "echo %s|passwd --stdin %s" % (passwd,username)
            if passwd == passwd1:
                c = salt.client.LocalClient()
                minions = c.run_job(saltid,'cmd.run',['echo'])['minions']
                ret1 = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
                retok = [ret[0] for ret in ret1.items() if "successfully" in ret[1]]
                execerr = list(set(minions).difference(set(retok)))
                total = len(minions)
                errnum = len(execerr)
                execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
                #if username == 'root':
                #    for i in ret1.keys():
                #        Hosts.objects.filter(saltid=i).update(passwd=passwd)
                if username in users:
                    Users.objects.filter(username=username).update(passwd=passwd)
                else:
                    Users.objects.create(username=username,passwd=passwd)
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='chpasswd',cmd=cmd,execerr=execerr,logret=ret1)
            else:
                ret1 = {"two passwd do not match!!!":''}
    return render_to_response('sysuser.html', locals())

@login_required
def install(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    #ips = [row['ip'] for row in Hosts.objects.values('ip')]
    install_dir = upload_dir + 'install'
    #files = os.listdir(install_dir)
    softs = [file for file in os.listdir(install_dir) if os.path.isfile("%s/%s" % (install_dir,file))]
    #softs = [row['soft'] for row in Soft.objects.values('soft')]
    if request.method == 'POST':
        if request.POST.has_key("install"):
            saltid = request.POST.get('saltid','')
            software = request.POST.get('software','')
            cmd = "wget %s/install/%s -O /tmp/%s >/dev/null 2>&1 && sh /tmp/%s >/dev/null 2>&1 && echo 'Install Success !!!'" % (download_url,software,software,software)
            def execcmd():
                c = salt.client.LocalClient()
                Deploylog.objects.create(name=software,saltid=saltid)
                id = Deploylog.objects.order_by('-id')[0].id
                rets = c.cmd(saltid,'cmd.run',[cmd],timeout=999)
                minions = c.run_job(saltid,'cmd.run',['echo'])['minions']
                retok = [ret[0] for ret in rets.items() if "Success" in ret[1]]
                execerr = list(set(minions).difference(set(retok)))
                total = len(minions)
                errnum = len(execerr)
                execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='install',cmd=cmd,execerr=execerr,logret=rets)
                endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                Deploylog.objects.filter(id=id).update(status='已完成',deployret=execerr,endtime=endtime)
            threading.Thread(target=execcmd).start()
            time.sleep(1)
    deployrets = Deploylog.objects.order_by('-id')[0:7]
    return render_to_response('install.html',locals())

@login_required
def optlog(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    ONE_PAGE_OF_DATA = pagelimit
    curPage = int(request.GET.get('curPage', '1'))
    allPage = int(request.GET.get('allPage','1'))
    pageType = str(request.GET.get('pageType', ''))
    if pageType == 'pageDown':
        curPage += 1
    elif pageType == 'pageUp':
        curPage -= 1

    startPos = (curPage - 1) * ONE_PAGE_OF_DATA
    endPos = startPos + ONE_PAGE_OF_DATA
    posts = Log.objects.filter(user=user).order_by('-alter_time')[startPos:endPos]
    if curPage == 1 and allPage == 1: 
        allPostCounts = Log.objects.filter(user=user).count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
                allPage += 1
    return render_to_response('optlog.html', locals())

def memcached_test(request):
    cache_key = "myID"
    result = cache.get(cache_key)
    if result is None:
        data = "hello, found"
        cache.set(cache_key, data, 60)
        return HttpResponse("not found")
    else:
        return HttpResponse(result)

def testpage(request):
    return render_to_response('load.html',locals())

def ajax_test(request):
    user = request.user 
    username = 'feilong'
    if request.method == 'GET':
        username = request.GET['username']
    if username == 'feilong':
        message = "no"
    else: 
        message = "yes"
    return HttpResponse(message)

@login_required
def todolist(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    todolist = Todo.objects.filter(flag=1)
    #todolist = Todo.objects.filter(flag=1).order_by('-pubtime')
    finishtodos = Todo.objects.filter(flag=0)
    #finishtodos = Todo.objects.filter(flag=0).order_by('-pubtime')
    return render_to_response('simpleTodo.html',locals())
                                                        
def todofinish(request, id=""):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    todo = Todo.objects.get(id=id)
    if todo.flag == "1":
        todo.flag = '0'
        todo.save()
        return HttpResponseRedirect('/salt/todo/')
    todolist = Todo.objects.filter(flag=1)
    finishtodos = Todo.objects.filter(flag=0)
    return render_to_response('simpleTodo.html',locals())
                                                        
def todoback(request, id=""):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    todo = Todo.objects.get(id=id)
    if todo.flag == '0':
        todo.flag = 1
        todo.save()
        return HttpResponseRedirect('/salt/todo/')
    todolist = Todo.objects.filter(flag=1)
    finishtodos = Todo.objects.filter(flag=0)
    return render_to_response('simpleTodo.html',locals())
                                                        
def tododelete(request, id=""):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    try:
        todo = Todo.objects.get(id=id)
    except Exception:
        raise  Http404
                                                        
    if todo:
        todo.delete()
        return HttpResponseRedirect('/salt/todo/')
    todolist = Todo.objects.filter(flag=1)
    finishtodos = Todo.objects.filter(flag=0)
    return render_to_response('simpleTodo.html',locals())
                                                        
def todoadd(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        atodo = request.POST['todo']
        priority = request.POST['priority']
        todo = Todo(user=user, todo=atodo, priority=priority, flag='1')
        todo.save()
        return HttpResponseRedirect('/salt/todo/')
    else:
        return render_to_response('addTodo.html',locals())
                                                            
                                                            
def todoupdate(request, id=''):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        atodo = request.POST['todo']
        priority = request.POST['priority']
        todo = Todo.objects.filter(id=id).update(todo=atodo,priority=priority)
        return HttpResponseRedirect('/salt/todo/')
    else:
        todo = Todo.objects.get(id=id)
        return render_to_response("updateTodo.html",locals())

def address(request):
    UNRULY_PASSENGERS = [146,184,235,200,226,251,299,273,281,304,203]
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=unruly.csv'
    writer = csv.writer(response)
    writer.writerow(['Year', 'Unruly Airline Passengers'])
    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
        writer.writerow([year, num])
    return response

@login_required
def msg(request):
    user = request.user
    users = User.objects.all()
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    rets = Msg.objects.filter(msgto=user).order_by("-pubtime")
    if request.method == 'POST':
        username = request.POST['user']
        msgtitle = request.POST['msgtitle']
        content = request.POST['content']
        Msg.objects.create(msgfrom=user,msgto=username,title=msgtitle,content=content)
    return render_to_response('msg.html',locals())

def readmsg(request, id=''):
    user = request.user
    ret = Msg.objects.get(id=id)
    Msg.objects.filter(id=id).update(isread=1)
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    return render_to_response('readmsg.html',locals())

def delmsg(request, id=''):
    Msg.objects.filter(id=id).delete()
    return HttpResponseRedirect('/salt/msg/')

@login_required
def groups(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        groupname = request.POST['groupname']
        hosts = request.POST['hosts']
        if request.POST.has_key("add"):
            os.popen('echo "    %s: %s" >> %s' % (groupname,hosts,groupsconf))
        if request.POST.has_key("modf"):
            os.popen('sed -i "s/%s:.*/%s: %s/" %s' % (groupname,groupname,hosts,groupsconf))
        if request.POST.has_key("del"):
            os.popen('sed -i "/%s:.*/d" %s' % (groupname,groupsconf))
    a = file(groupsconf).readlines()
    a.remove('nodegroups:\n')
    rets = {}
    for i in a:
        groupname = i.rstrip('\n').strip().split(':')[0]
        hosts = i.rstrip('\n').strip().split(':')[1]
        rets[groupname] = hosts
    return render_to_response('groups.html',locals())
