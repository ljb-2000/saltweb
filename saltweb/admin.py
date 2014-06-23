#!/usr/bin/env python
#coding=utf-8
#author: hhr
from django.contrib import admin
from saltweb.models import *
from saltweb.models import Todo

class HostsAdmin(admin.ModelAdmin):
    list_display = ('saltid','ip','hostname','host_type','mem','os','sn','model','disk','updatetime','mark','pingstatus','saltstatus','num','nowtime','lasttime','sendmail','closemail')
    ordering = ('nowtime',)
    search_fields = ('saltid', 'hostname')
class UsersAdmin(admin.ModelAdmin):
    list_display = ('username','passwd')
#class MonitorAdmin(admin.ModelAdmin):
#    list_display = ('saltid','ip','pingstatus','saltstatus','num','nowtime','lasttime','sendmail','closemail')
#    ordering = ('saltstatus',)
class MastermonitorAdmin(admin.ModelAdmin):
    list_display = ('saltid','ip','num','status','nowtime','lasttime','sendmail','closemail')
class UploadAdmin(admin.ModelAdmin):
    list_display = ('name','file')
class LogAdmin(admin.ModelAdmin):
    list_display = ('user','saltid','ip','logtype','cmd','execerr','logret','nowtime')
    ordering = ('-nowtime',)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('user', 'todo', 'priority', 'flag', 'nowtime')
    ordering = ('-nowtime',)
#class MonitortypeAdmin(admin.ModelAdmin):
#    list_display = ('name','alias')
class ChagelogAdmin(admin.ModelAdmin):
    list_display = ('saltid','ip','chage','nowtime')
class MsgAdmin(admin.ModelAdmin):
    list_display = ('msgfrom','msgto','title','content','isread','nowtime')
    ordering = ('-nowtime',)
class UrlAdmin(admin.ModelAdmin):
    list_display = ('proname','domainname','ip','port','urlname','contact','status','num','nowtime','lasttime','sendmail','closemail')
    ordering = ('-nowtime',)
class DeploylogAdmin(admin.ModelAdmin):
    list_display = ('name','saltid','ip','starttime','status','deployret','endtime')
    ordering = ('-id',)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('hostid','msg','to','nowtime')
    ordering = ('-id',)
class MinionslogAdmin(admin.ModelAdmin):
    list_display = ('name','saltid','ip','starttime','status','deployret','endtime')
    ordering = ('-id',)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name','hosts','contact','nowtime')
    ordering = ('-id',)

#admin.site.register(Pro_type)
admin.site.register(Users,UsersAdmin)
admin.site.register(Hosts,HostsAdmin)
#admin.site.register(Monitor,MonitorAdmin)
admin.site.register(Mastermonitor,MastermonitorAdmin)
admin.site.register(Upload,UploadAdmin)
admin.site.register(Log,LogAdmin)
#admin.site.register(Soft)
admin.site.register(Todo,TodoAdmin)
#admin.site.register(Monitortype,MonitortypeAdmin)
admin.site.register(Chagelog,ChagelogAdmin)
#admin.site.register(Address)
admin.site.register(Msg,MsgAdmin)
admin.site.register(Url,UrlAdmin)
admin.site.register(Deploylog,DeploylogAdmin)
admin.site.register(Alarm,AlarmAdmin)
admin.site.register(Minionslog,MinionslogAdmin)
admin.site.register(Group,GroupAdmin)
