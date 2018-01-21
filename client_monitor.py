import time
import ast
import socket
import sys
import os

webserverips = ['10.10.3.137']
cputhreshold_min = 10
cputhreshold_max = 40
port = 8443

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

def scaleup(total_containers):
    total_containers+=1
    os.system('docker service scale cloudapp='+str(total_containers))

def scaledown(factor):
    if factor == 0:
        return
    os.system('docker service scale cloudapp='+str(factor))

def monitor(serverstats,total_containers):
    scaledownfactor = 0
    for ip in serverstats:
        for container in serverstats[ip]:
            cpu = serverstats[ip][container]
            if cpu > cputhreshold_max:
               scaleup(total_containers)
               return
            elif cpu < cputhreshold_min:
                scaledownfactor+=1
    if total_containers == 1:
        return
    if scaledownfactor > 0:
        if total_containers == scaledownfactor:
            scaledown(1)
        else:
            scaledown(total_containers - scaledownfactor)
    return

def main():
    serverstats = {}
    while(1):
        total_containers = 0
        for i in webserverips:
            msg = 'status'
            try :
                s.sendto(msg, (i, port))
                d = s.recvfrom(1024)
                reply = d[0]
                addr = d[1]
                print 'Server reply : ' , ast.literal_eval(reply)
                serverstats[addr] = ast.literal_eval(reply)
                total_containers+=len(ast.literal_eval(reply))

            except socket.error, msg:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                continue
        monitor(serverstats,total_containers)
        time.sleep(6)
main()
