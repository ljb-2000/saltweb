#!/usr/bin/python
import time,os,sys
import rrdtool
import comm
import salt

c = salt.client.LocalClient() 
loadcmd = "cat /proc/loadavg |awk '{print $1}'"
connumcmd = "netstat -n|awk '/^tcp/ {++S[$NF]} END {for (a in S) print a,S[a]}'|grep ESTABLISHED|awk '{print $2}'"
try:
    loadrets = c.cmd('*','cmd.run',[loadcmd],timeout=5) 
except:
    sys.exit()
connumrets = c.cmd('*','cmd.run',[connumcmd],timeout=5) 
for (id,ret) in loadrets.items():
    rrdfile = comm.rrd_dir + id + '/load.rrd'
    if os.path.isfile(rrdfile):
        rrdtool.update(rrdfile,'N:%.2f' % float(ret))
for (id,ret) in connumrets.items():
    rrdfile = comm.rrd_dir + id + '/connum.rrd'
    if os.path.isfile(rrdfile):
        rrdtool.update(rrdfile,'N:%d' % int(ret))
