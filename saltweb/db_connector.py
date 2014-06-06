#!/usr/bin/env python
#coding=utf-8
#author: hhr
#db_connect
import sys,os,time
from comm import base_dir
sys.path.append(base_dir) #工作目录
os.environ['DJANGO_SETTINGS_MODULE'] ='saltweb.settings'
from saltweb import settings
#from saltweb.models import *
