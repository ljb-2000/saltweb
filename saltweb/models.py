#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django.db.models import *
from django.contrib.auth.models import User
from saltweb.comm import *

#非root账号密码表，所有服务器账号密码统一
class Users(Model):
    username = CharField(max_length=50,default='hhr')
    passwd = CharField(max_length=50,default='123')

class Hosts(Model):
    saltid = CharField(max_length=50)
    hostname = CharField(max_length=50)
    ip = IPAddressField(unique=True)
    port = IntegerField(default=sshdefaultport)
    host_type = CharField(max_length=50,default='虚拟机')
    #user = CharField(max_length=50,default='root')
    #passwd = CharField(max_length=50,default='123')
    os = CharField(max_length=50)
    mem = CharField(max_length=50)
    #protocol_type = ForeignKey(Pro_type)
    cpu = CharField(max_length=50,blank=True)
    cpunum = IntegerField()
    model = CharField(max_length=50,default='Null')
    sn = CharField(max_length=50,default='Null')
    disk = CharField(max_length=50,default='Null')
    mark = CharField(max_length=100,blank=True)
    nowtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.ip

class Monitor(Model):
    saltid = CharField(max_length=50)
    ip = IPAddressField()
    pingstatus = CharField(max_length=10,blank=True)
    saltstatus = CharField(max_length=10,blank=True)
    num = IntegerField(default=0)
    nowtime = CharField(max_length=100,blank=True)
    lasttime = CharField(max_length=100,blank=True)
    sendmail = IntegerField(default=0)
    closemail = IntegerField(default=0)
    def __unicode__(self):
        return self.saltid

class Mastermonitor(Model):
    saltid = CharField(max_length=50,default='saltwebmaster')
    ip = IPAddressField()
    status = CharField(max_length=10,blank=True)
    num = IntegerField(default=0)
    nowtime = CharField(max_length=100,blank=True)
    lasttime = CharField(max_length=100,blank=True)
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
    nowtime = DateTimeField(auto_now_add=True)
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
    nowtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return u'%d %s %s' % (self.id, self.todo, self.flag)
    class Meta:
        ordering = ['priority', 'nowtime']

#class Monitortype(Model):
#    name = CharField(max_length=50)
#    alias = CharField(max_length=50)
#    def __unicode__(self):
#        return self.name

class Chagelog(Model):
    saltid = CharField(max_length=50)
    ip = CharField(max_length=50)
    chage = CharField(max_length=255)
    nowtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.saltid

class Msg(Model):
    msgfrom = CharField(max_length=50)
    msgto = CharField(max_length=50)
    title = CharField(max_length=100)
    content = TextField(max_length=500)
    nowtime = DateTimeField(auto_now_add=True)
    isread = IntegerField(default=0)
    def __unicode__(self):
        return self.title

class Url(Model):
    proname = CharField(max_length=50,unique=True)
    domainname = CharField(max_length=50)
    ip = CharField(max_length=50)
    port = IntegerField()
    urlname = CharField(max_length=100)
    contact = CharField(max_length=100)
    status = CharField(max_length=10)
    num = IntegerField(default=0)
    nowtime = CharField(max_length=100,blank=True)
    lasttime = CharField(max_length=100,blank=True)
    sendmail = IntegerField(default=0)
    closemail = IntegerField(default=0)
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

class Group(Model):
    name = CharField(max_length=50)
    hosts = CharField(max_length=500)
    contact = CharField(max_length=500)
    nowtime = DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name
