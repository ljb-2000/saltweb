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
    masterstatus = Mastermonitor.objects.get(id=1).status
    up = Monitor.objects.filter(saltstatus='True').count()
    down = Monitor.objects.filter(saltstatus='False').count()
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
    posts = Monitor.objects.order_by("saltstatus")[startPos:endPos]
    if curPage == 1 and allPage == 1: 
        allPostCounts = Monitor.objects.count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
                allPage += 1
    id = request.GET.get('id',)
    closemail = request.GET.get('closemail',)
    Monitor.objects.filter(id=id).update(closemail=closemail)
    allclosemail = request.GET.get('allclosemail',)
    if allclosemail:
        Monitor.objects.all().update(closemail=allclosemail)
    return render_to_response('monitor.html',locals())


@login_required
def alarm(request):
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
    posts = Alarm.objects.order_by('-id')[startPos:endPos]
    if curPage == 1 and allPage == 1:
        allPostCounts = Alarm.objects.count()
        allPage = allPostCounts / ONE_PAGE_OF_DATA
        remainPost = allPostCounts % ONE_PAGE_OF_DATA
        if remainPost > 0:
                allPage += 1
    return render_to_response('alarm.html',locals())


@login_required
def assets(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    saltids = [row['saltid'] for row in Hosts.objects.order_by("saltid").values('saltid')]
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
        posts = Hosts.objects.order_by("saltid")[startPos:endPos]
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
    saltids = [row['saltid'] for row in Hosts.objects.order_by("saltid").values('saltid')]
    if os.system("/etc/init.d/salt-master status >/dev/null") != 0:
        msg = "salt-master服务未启动"
    elif request.method == 'POST':
        c = salt.client.LocalClient()
        port = sshdefaultport
        username = request.POST.get('username','')
        passwd = request.POST.get('passwd','')
        if request.POST.has_key("madd"):
            hosts = request.POST.get('hosts','')
            if '-' in hosts and ',' not in hosts:
                start = hosts.split('-')[0].split('.')[3]
                end = hosts.split('-')[1]
                ip = hosts.split('-')[0].split('.')[ : 3]
                ip3 = '.'.join(ip)
                for ip1 in xrange(int(start), int(end) + 1):
                    host = ip3 + '.' + str(ip1)
                    cmd = cmdminion(host)
                    def sshfc(host):
                        Minionslog.objects.create(name='add_minion',ip=host)
                        id = Minionslog.objects.order_by('-id')[0].id
                        ret = ssh(host,port,username,passwd,cmd)
                        endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                        Minionslog.objects.filter(id=id).update(status='已完成',deployret=ret[host],endtime=endtime)
                    threading.Thread(target=sshfc,args=(host,)).start()
                    time.sleep(1)
                    
            if ',' in hosts and '-' not in hosts:
                hosts = hosts.split(',')
                for host in hosts:
                    cmd = cmdminion(host)
                    def sshfc(host):
                        Minionslog.objects.create(name='add_minion',ip=host)
                        id = Minionslog.objects.order_by('-id')[0].id
                        ret = ssh(host,port,username,passwd,cmd)
                        endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                        Minionslog.objects.filter(id=id).update(status='已完成',deployret=ret[host],endtime=endtime)
                    threading.Thread(target=sshfc,args=(host,)).start()
                    time.sleep(1)
            if ',' in hosts and '-' in hosts:
                msg = "iplist填写不符合，请参考说明重新填写，谢谢！"
        if request.POST.has_key("add"):
            host = request.POST.get('host','')
            cmd = cmdminion(host)
            def sshfc(host):
                Minionslog.objects.create(name='add_minion',ip=host)
                id = Minionslog.objects.order_by('-id')[0].id
                ret = ssh(host,port,username,passwd,cmd)
                endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                Minionslog.objects.filter(id=id).update(status='已完成',deployret=ret[host],endtime=endtime)
            threading.Thread(target=sshfc,args=(host,)).start()
            time.sleep(1)   
        if request.POST.has_key("del"):
            minions = c.run_job('*','cmd.run',['echo'],expr_form='glob')['minions']
            saltid = request.POST.get('saltid','') 
            Minionslog.objects.create(name='del_minion',saltid=saltid)
            id = Minionslog.objects.order_by('-id')[0].id
            if saltid == "all":
                cmd = 'sed -i "s/^master/#master/g" /etc/salt/minion'
                cmd += '&& /etc/init.d/salt-minion stop >/dev/null'
                cmd += "&& echo 'Success'"
                ret = c.cmd("*",'cmd.run',[cmd],timeout=5)
                os.system('salt-key -D -y' )
                Hosts.objects.all().delete()
                Monitor.objects.all().delete()
                endtime = time.strftime("%Y-%m-%d %H:%M:%S")
                execerr = list(set(minions).difference(set(ret.keys())))
                total = len(minions)
                errnum = len(execerr)
                execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
                if len(execerr) > 950: execerr = execerr[:950]+'...'
                Minionslog.objects.filter(id=id).update(status='已完成',deployret=execerr,endtime=endtime)
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='del_minion',execerr=execerr)
                return HttpResponseRedirect('/salt/minions/')
            cmd = 'sed -i "s/^master/#master/g" /etc/salt/minion'
            cmd += '&& /etc/init.d/salt-minion stop >/dev/null'
            cmd += "&& echo 'Success'"
            ret = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
            if ret:
                ret = 'Success'
                saltids = [row['saltid'] for row in Hosts.objects.order_by("saltid").values('saltid')]
            else:
                ret = 'Error: minion 宕机或者salt-minion服务未开启'
            os.system('salt-key -d %s -y' % saltid )
            Hosts.objects.filter(saltid=saltid).delete()
            Monitor.objects.filter(saltid=saltid).delete()
            endtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Minionslog.objects.filter(id=id).update(status='已完成',deployret=ret,endtime=endtime)
            Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='del_minion',execerr=ret)
            return HttpResponseRedirect('/salt/minions/')
    deployrets = Minionslog.objects.order_by('-id')[0:7]
    return render_to_response('minions.html',locals())

@login_required
def urlmonitor(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        if request.POST.has_key("add"):
            proname = request.POST.get('proname','')
            urlname = request.POST.get('urlname','')
            contact = request.POST.get('contact','')
            ip = request.POST.get('ip','')
            port = request.POST.get('port','')
            r = curl(urlname,ip,port)
            proname = proname + '-' + ip
            nowtime = time.strftime("%Y-%m-%d %X")
            if not Url.objects.filter(proname=proname) and urlname.startswith('http://'):
                Url.objects.create(proname=proname,contact=contact,ip=ip,port=port,urlname=urlname,domainname=r[0],nowtime=nowtime,status=r[1])
            else: 
                msg = '工程名已存在或者url地址不是以http开头'
        if request.POST.has_key("search"):
            re = request.POST.get('searchproname','')
            if re:
                pronames = [row['proname'] for row in Url.objects.values('proname')]
                rets = [Url.objects.get(proname=i) for i in pronames if re in i]
                return render_to_response('urlmonitor.html',locals())
    updateall = request.GET.get('updateall',)
    if updateall:
        os.popen('python %ssaltweb/urlmonitor.py' % base_dir)
    id = request.GET.get('id',)
    urlupdate = request.GET.get('urlupdate',)
    urldel = request.GET.get('urldel',)
    closemail = request.GET.get('closemail',)
    allclosemail = request.GET.get('allclosemail',)
    if urlupdate:
        ret = Url.objects.get(id=id)
        urlname = ret.urlname
        ip = ret.ip
        port = ret.port
        r = curl(urlname,ip,port)
        nowtime = time.strftime("%Y-%m-%d %X")
        Url.objects.filter(id=id).update(domainname=r[0],status=r[1],nowtime=nowtime)
    if urldel:
        Url.objects.filter(id=id).delete()
    if allclosemail:
        Url.objects.all().update(closemail=allclosemail)
    if closemail:
        Url.objects.filter(id=id).update(closemail=closemail)
    rets = Url.objects.order_by("-status")
    return render_to_response('urlmonitor.html',locals())

@login_required
def chagelog(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    rets = Chagelog.objects.order_by("-nowtime")
    return render_to_response('chagelog.html',locals())

@login_required
def saltcmd(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    dangercmd = ",".join(dangercmdlist)
    if os.system("/etc/init.d/salt-master status >/dev/null") != 0:
        msg = "salt-master服务未启动"
    elif request.method == 'POST':	
        c = salt.client.LocalClient()
        saltid = request.POST.get('saltid','')
        fun = request.POST.get('fun','')
        cmd = request.POST.get('cmd','')
        type = request.POST.get('type','')
        minions = c.run_job(saltid,'cmd.run',['echo'],expr_form=type)['minions']
        dangercmds = [i for i in dangercmdlist if i in cmd]
        if not dangercmds:
            ret1 = c.cmd(saltid,fun,[cmd],expr_form=type,timeout=99)
            execerr = list(set(minions).difference(set(ret1.keys())))
            total = len(minions)
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
            if len(execerr) > 950: execerr = execerr[:950]+'...'
            Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype=fun,cmd=cmd,execerr=execerr)
        else:
            msg = '包含危险命令%s关键字，禁止执行' % str(dangercmdlist)    
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
            ret1 = ret1.decode('utf8')
            total = len(ret1)
            execerr = [','.join(i.keys()) for i in ret1 if ','.join(i.values()).startswith('Error:')]
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
            if len(execerr) > 950: execerr = execerr[:950]+'...'
            Log.objects.create(user=str(user),ip=host,saltid='-',logtype='ssh',cmd=cmd,execerr=execerr)
        elif host.startswith(network_list):
            port = Hosts.objects.get(ip=host).port
            username = request.POST.get('username','')
            passwd = Users.objects.get(username=username).passwd
            cmd = request.POST.get('cmd','')
            ret1 = [ssh(host,int(port),username,passwd,cmd)]
            execerr = [','.join(i.keys()) for i in ret1 if ','.join(i.values()).startswith('Error:')]
            errnum = len(execerr)
            execerr = 'total:1 errnum:%d errret:%s' % (errnum,','.join(execerr))
            if len(execerr) > 950: execerr = execerr[:950]+'...'
            Log.objects.create(user=str(user),ip=host,saltid='-',logtype='ssh',cmd=cmd,execerr=execerr)
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
    #files = os.listdir(upload_dir)
    files = os.popen('cd %s ;find . -type f' % upload_dir).read().strip("./").strip("\n").split('\n./')
    return render_to_response('upload.html', locals())

@login_required
def editfile(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    if request.method == 'POST':
        if request.POST.has_key("new"):
            name = request.POST.get('name','').strip()
            if os.path.isfile(upload_dir + name):
                f = open(upload_dir + name)
                data = f.read()
                f.close()
            else:
                msg = "文件不存在!!!"
        if request.POST.has_key("edit"):
            name = request.POST.get('name','').strip()
            if os.path.isfile(upload_dir + name):
                data = request.POST.get('data','')
                filename = upload_dir + name
                fp = file(upload_dir + name,'wb')
                fp.write(data)
                data = ''
                name = ''
                fp.close()
                msg = "修改成功!!!"
            else:
                msg = "文件不存在!!!"
            Log.objects.create(user=str(user),ip='localhost',saltid='-',logtype='editfile',cmd=filename,execerr=msg)
    uploaddir = upload_dir
    files = os.popen('cd %s ;find . -type f' % upload_dir).read().strip("./").strip("\n").split('\n./')
    return render_to_response('editfile.html', locals())

@login_required
def syncfile(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    #files = [file for file in os.listdir(upload_dir) if os.path.isfile("%s/%s" % (upload_dir,file))]
    files = os.popen('cd %s ;find . -type f' % upload_dir).read().strip("./").strip("\n").split('\n./')
    if os.system("/etc/init.d/salt-master status >/dev/null") != 0:
        msg = "salt-master服务未启动"
    elif request.method == 'POST':
        filename = request.POST.get('filename','')
        local = upload_dir + filename
        remote = request.POST.get('path','')
        saltid = request.POST.get('saltid','')
        cmd = 'wget %s%s -O %s >/dev/null 2>&1 && echo "saltexec_ok !!!"' % (download_url,filename,remote)
        c = salt.client.LocalClient()
        rets = c.cmd(saltid,'cmd.run',[cmd],timeout=5)
        minions = c.run_job(saltid,'cmd.run',['echo'])['minions']
        retok = [ret[0] for ret in rets.items() if "saltexec_ok" in ret[1]]
        execerr = list(set(minions).difference(set(retok)))
        total = len(minions)
        errnum = len(execerr)
        execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
        if len(execerr) > 950: execerr = execerr[:950]+'...'
        #if len(str(ret1)) > 950:
        #    for k,v in ret1.items():
        #        if v == 'saltexec_ok':del ret1[k]
        Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='putfile',cmd=cmd,execerr=execerr)
    return render_to_response('syncfile.html', locals())

@login_required
def sysuser(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    users = [row.username for row in Users.objects.all()]
    if os.system("/etc/init.d/salt-master status >/dev/null") != 0:
        msg = "salt-master服务未开启"
    elif request.method == 'POST':
        if request.POST.has_key("adduser"):
            saltid = request.POST.get('saltid','')
            username = request.POST.get('username','')
            passwd = request.POST.get('passwd','')
            passwd1 = request.POST.get('passwd1','')
            usertype = request.POST.get('usertype','')
            if passwd == passwd1:
                cmd = "useradd %s >/dev/null 2>&1 ;echo %s|passwd --stdin %s >/dev/null 2>&1 &&echo 'successfully'" % (username,passwd,username)
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
                if len(execerr) > 950: execerr = execerr[:950]+'...'
                if username in users:
                    Users.objects.filter(username=username).update(passwd=passwd)
                else:
                    Users.objects.create(username=username,passwd=passwd)
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='adduser',cmd=cmd,execerr=execerr)
            else:
                msg = "两次密码不一致"
        if request.POST.has_key("deluser"):
            saltid = request.POST.get('saltid','')
            username = request.POST.get('username','') 
            c = salt.client.LocalClient()
            minions = c.run_job(saltid,'cmd.run',['echo'])['minions'] 
            cmd = "userdel %s >/dev/null 2>&1 ;echo 'successfully'" % username
            ret1 = c.cmd(saltid,'cmd.run',[cmd],timeout=5)      
            retok = [ret[0] for ret in ret1.items() if "successfully" in ret[1]]
            execerr = list(set(minions).difference(set(retok)))
            total = len(minions)
            errnum = len(execerr)
            execerr = 'total:%d errnum:%d errret:%s' % (total,errnum,','.join(execerr))
            if len(execerr) > 950: execerr = execerr[:950]+'...'
            if username in users:
                Users.objects.filter(username=username).delete()
            Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='deluser',cmd=cmd,execerr=execerr)
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
                if len(execerr) > 950: execerr = execerr[:950]+'...'
                if username in users:
                    Users.objects.filter(username=username).update(passwd=passwd)
                else:
                    Users.objects.create(username=username,passwd=passwd)
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='chpasswd',cmd=cmd,execerr=execerr)
            else:
                msg = "两次密码不一致"
    return render_to_response('sysuser.html', locals())

@login_required
def install(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    install_dir = upload_dir + 'install'
    softs = [file for file in os.listdir(install_dir) if os.path.isfile("%s/%s" % (install_dir,file))]
    if os.system("/etc/init.d/salt-master status >/dev/null") != 0:
        msg = "salt-master服务未启动"
    elif request.method == 'POST':
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
                if len(execerr) > 950: execerr = execerr[:950]+'...'
                Log.objects.create(user=str(user),ip='-',saltid=saltid,logtype='install',cmd=cmd,execerr=execerr)
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
    posts = Log.objects.filter(user=user).order_by('-nowtime')[startPos:endPos]
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

@login_required
def todo(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    id = request.GET.get('id',)
    delete = request.GET.get('delete',)
    finish = request.GET.get('finish',)
    back = request.GET.get('back',)
    edit = request.GET.get('edit',)
    add = request.GET.get('add',)
    if finish:
        Todo.objects.filter(id=id).update(flag=0)
    if back:
        Todo.objects.filter(id=id).update(flag=1)
    if delete:
        Todo.objects.filter(id=id).delete()
    if edit:
        if request.method == 'POST':
            atodo = request.POST['todo']
            priority = request.POST['priority']
            todo = Todo.objects.filter(id=id).update(todo=atodo,priority=priority)
            return HttpResponseRedirect('/salt/todo/')
        else:
            todo = Todo.objects.get(id=id)
            return render_to_response("updatetodo.html",locals())
    if add:
        if request.method == 'POST':
            atodo = request.POST['todo']
            priority = request.POST['priority']
            todo = Todo.objects.create(user=user, todo=atodo, priority=priority, flag='1')
            return HttpResponseRedirect('/salt/todo/')   
        else:
            return render_to_response('updatetodo.html',locals())     
    todolist = Todo.objects.filter(flag=1)
    #todolist = Todo.objects.filter(flag=1).order_by('-pubtime')
    finishtodos = Todo.objects.filter(flag=0)
    #finishtodos = Todo.objects.filter(flag=0).order_by('-pubtime')
    return render_to_response('todo.html',locals())
                                                        

@login_required
def msg(request):
    user = request.user
    users = User.objects.all()
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    rets = Msg.objects.filter(msgto=user).order_by("-nowtime")
    id = request.GET.get('id',)
    delmsg = request.GET.get('delmsg',)
    readmsg = request.GET.get('readmsg',)
    isread = request.GET.get('isread',)
    allreadmsg = request.GET.get('allreadmsg',)
    alldelmsg = request.GET.get('alldelmsg',)
    if delmsg:
        Msg.objects.filter(id=id).delete()
    if readmsg:
        Msg.objects.filter(id=id).update(isread=1)
    if isread:
        ret = Msg.objects.get(id=id)
        Msg.objects.filter(id=id).update(isread=1)
        msgnum = Msg.objects.filter(isread=0,msgto=user).count()
        return render_to_response('readmsg.html',locals())
    if allreadmsg:
        Msg.objects.filter(msgto=str(user)).update(isread=1)
    if alldelmsg:
        Msg.objects.filter(msgto=str(user)).delete()
    if request.method == 'POST':
        username = request.POST['user']
        msgtitle = request.POST['msgtitle']
        content = request.POST['content']
        if username == 'all':
            for u in users:
                Msg.objects.create(msgfrom=user,msgto=u,title=msgtitle,content=content)
        else:
            Msg.objects.create(msgfrom=user,msgto=username,title=msgtitle,content=content)
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    return render_to_response('msg.html',locals())

@login_required
def groups(request):
    user = request.user
    msgnum = Msg.objects.filter(isread=0,msgto=user).count()
    name = request.GET.get('name',)
    hosts = request.GET.get('hosts',)
    contact = request.GET.get('contact',)
    edit = request.GET.get('edit',)
    delete = request.GET.get('delete',)
    if delete:
        os.popen('sed -i "/%s:.*/d" %s' % (name,groupsconf)) 
        Group.objects.filter(name=name).delete()
        return HttpResponseRedirect('/salt/groups/')
    if edit:
        if request.method == 'POST':
            name = request.POST['name']
            hosts = request.POST['hosts']
            contact = request.POST['contact']
            os.popen('sed -i "s/%s:.*/%s: %s/" %s' % (name,name,hosts,groupsconf))
            nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
            Group.objects.filter(name=name).update(hosts=hosts,contact=contact,nowtime=nowtime)        
            return HttpResponseRedirect('/salt/groups/')
        else:
            ret = Group.objects.get(name=name)
            return render_to_response("updategroups.html",locals())
    if request.method == 'POST':
        groupname = request.POST['groupname']
        hosts = request.POST['hosts']
        contact = request.POST['contact']
        if request.POST.has_key("add"):
            if not Group.objects.filter(name=groupname):
                os.popen('echo "    %s: %s" >> %s' % (groupname,hosts,groupsconf))
                Group.objects.create(name=groupname,hosts=hosts,contact=contact)
            else:
                msg = "组名已经存在"
        if request.POST.has_key("modf"):
            if Group.objects.filter(name=groupname):
                os.popen('sed -i "s/%s:.*/%s: %s/" %s' % (groupname,groupname,hosts,groupsconf))
                nowtime = time.strftime("%Y-%m-%d %H:%M:%S")
                Group.objects.filter(name=groupname).update(hosts=hosts,contact=contact,nowtime=nowtime)
            else:
                msg = "组名不存在"
    rets = Group.objects.all()
    return render_to_response('groups.html',locals())
