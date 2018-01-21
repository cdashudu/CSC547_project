import logging
import docker
import os
import sys
import time
import socket

def cpu_stats(cont):
    data =  {}
    for con in cont:
        if con.status!='running':
            print "Container not running"
            continue
        constat = con.stats(stream=False)
        prestats = constat['precpu_stats']
        cpustats = constat['cpu_stats']
        prestats_totalusage = prestats['cpu_usage']['total_usage']
        stats_totalusage = cpustats['cpu_usage']['total_usage']
        numOfCPUCore = len(cpustats['cpu_usage']['percpu_usage'])
        prestats_syscpu = prestats['system_cpu_usage']
        stats_syscpu = cpustats['system_cpu_usage']
        cpuDelta = stats_totalusage - prestats_totalusage
        systemDelta = stats_syscpu - prestats_syscpu
        cpupercentage = 0.0
        if cpuDelta > 0 and systemDelta > 0:
            cpupercentage = float(cpuDelta*numOfCPUCore*100) / float(systemDelta)
        if 'cloudapp' in con.name:
            data[con.name] = cpupercentage
    return data

host = 'localhost'
port = 8443
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", port))
while 1:
    data, addr = s.recvfrom(1024)
    cli=docker.DockerClient(base_url='unix://var/run/docker.sock',version='auto')
    cont=cli.containers.list()
    msg = cpu_stats(cont)
    s.sendto(str(msg),addr)
    time.sleep(2)
