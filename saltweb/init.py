#!/usr/bin/env python
#coding=utf-8
#author: hhr
import os,sys,time,re
import threading
import comm, db_connector
from saltweb.models import *

Hosts.objects.all().delete()
Monitortype.objects.all().delete()
Mastermonitor.objects.all().delete()
