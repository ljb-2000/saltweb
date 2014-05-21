#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django.db.models import *
from django.contrib.auth.models import User
from saltweb.comm import *

class Pro_type(Model):
    name = CharField(max_length=50,default='SSH')
    def __unicode__(self):
        return self.name

#非root账号密码表，所有服务器账号密码统一
class Users(Model):
    username = CharField(max_length=50,default='hhr')
    passwd = CharField(max_length=50,default='123')
    #protocol_type = ForeignKey(Pro_type)
    #pkey_file = CharField(max_length=50,default='/home/hhr/.ssh/id_rsa')
class Hosts(Model):
    saltid = CharField(max_length=50)
    hostname = CharField(max_length=50)
    ip = IPAddressField(unique=True)
    host_type = CharField(max_length=50,default='虚拟机')
    user = CharField(max_length=50,default='root')
    passwd = CharField(max_length=50,default='123')
    mem = CharField(max_length=50)
    os = CharField(max_length=50)
    port = IntegerField(default=sshdefaultport)
    #protocol_type = ForeignKey(Pro_type)
    cpu = CharField(max_length=50,blank=True)
    cpunum = IntegerField()
    model = CharField(max_length=50,default='Null')
    sn = CharField(max_length=50,default='Null')
    disk = CharField(max_length=50,default='Null')
    mark = CharField(max_length=100,blank=True)
    update_date = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.ip

class Monitor(Model):
    saltid = CharField(max_length=50)
    ip = IPAddressField()
    pingstats = CharField(max_length=10,blank=True)
    saltstats = CharField(max_length=10,blank=True)
    load = CharField(max_length=50,blank=True)
    connum = CharField(max_length=100,blank=True)
    num = IntegerField(default=0)
    nowtime = CharField(max_length=100,blank=True)
    sendmail = IntegerField(default=0)
    closemail = IntegerField(default=0)
    def __unicode__(self):
        return self.saltid

class Mastermonitor(Model):
    saltid = CharField(max_length=50,default='saltwebmaster')
    ip = IPAddressField()
    #pingstats = CharField(max_length=10,blank=True)
    #saltstats = CharField(max_length=10,blank=True)
    #load = CharField(max_length=50,blank=True)
    connum = CharField(max_length=100,blank=True)
    num = IntegerField(default=0)
    nowtime = CharField(max_length=100,blank=True)
    sendmail = IntegerField(default=0)
    closemail = IntegerField(default=0)
    def __unicode__(self):
        return self.saltid

class Upload(Model):
    name = CharField(max_length=100)
    file = FileField(upload_to="./upload/");
    def __unicode__(self):
        return self.name

class Log(Model):
    user = CharField(max_length=50)
    saltid = CharField(max_length=50)
    ip = CharField(max_length=50)
    logtype = CharField(max_length=50)
    cmd = CharField(max_length=255)
    execerr = CharField(max_length=255)
    logret = TextField(max_length=1000)
    alter_time = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.saltid
class Soft(Model):
    soft = CharField(max_length=50)
    def __unicode__(self):
        return self.soft

class Todo(Model):
    user = ForeignKey(User)
    todo = CharField(max_length=50)
    flag = CharField(max_length=2, default='1')
    priority = CharField(max_length=2, default='0')
    pubtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return u'%d %s %s' % (self.id, self.todo, self.flag)
    class Meta:
        ordering = ['priority', 'pubtime']

class Monitortype(Model):
    name = CharField(max_length=50)
    alias = CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Chagelog(Model):
    saltid = CharField(max_length=50)
    ip = CharField(max_length=50)
    chage = CharField(max_length=255)
    updatetime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.saltid

class Address(Model): 
    name = CharField("姓名",max_length=32,unique=True) 
    gender = CharField("性别",choices=(("M","男"),("F","女")),max_length=1) 
    #telphone = CharField("电话",max_length=20) 
    mobile = CharField("手机",max_length=11) 
    room = CharField('房间', max_length=32) 
    def __unicode__(self): 
        return self.name 
class Msg(Model):
    msgfrom = CharField(max_length=50)
    msgto = CharField(max_length=50)
    title = CharField(max_length=50)
    content = TextField(max_length=500)
    pubtime = DateTimeField(auto_now_add=True)
    isread = IntegerField(default=0)
    def __unicode__(self):
        return self.title
class Url(Model):
    proname = CharField(max_length=50,unique=True)
    domainname = CharField(max_length=50)
    ip = CharField(max_length=50)
    port = IntegerField()
    urlname = CharField(max_length=100)
    pubtime = DateTimeField(auto_now_add=True)
    state = CharField(max_length=10)
    def __unicode__(self):
        return self.proname

class Deploylog(Model):
    name = CharField(max_length=50)
    ip = CharField(max_length=50)
    saltid = CharField(max_length=50)
    status = CharField(max_length=50,default='进行中')
    deployret = CharField(max_length=500)
    starttime = DateTimeField(auto_now_add=True)
    endtime = CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Monionslog(Model):
    name = CharField(max_length=50)
    ip = CharField(max_length=50)
    saltid = CharField(max_length=50)
    status = CharField(max_length=50,default='进行中')
    deployret = CharField(max_length=500)
    starttime = DateTimeField(auto_now_add=True)
    endtime = CharField(max_length=50)
    def __unicode__(self):
        return self.name

class Alarm(Model):
    hostid = CharField(max_length=50)
    msg = CharField(max_length=500)
    to = CharField(max_length=50)
    nowtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.hostid
