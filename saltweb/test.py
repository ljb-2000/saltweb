import salt
import sys, time
from comm import *
import db_connector
from django.core.mail import send_mail
from saltweb.models import *
import multiprocessing, threading

#msg = 'CRITICAL: test'
#title = 'saltwebmaster'
#f = "saltweb@hhr.com"
#t = ["huanghuirong@hudong.com"]
#send_mail(msg,title,f,t)
#send_mail(u'CRITICAL: salt-master down',u'saltwebmaster',comm.from_mail,comm.samail_list)
