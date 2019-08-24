import paramiko
import sys
import requests
import json
from flask import Flask,request
import socket
import os
import time

app = Flask(__name__)
config = 'config.json'

def read_config():
    with open(config) as f:
        d = json.load(f)
        mount_ip = d['mount_ip']
        mount_path = d['mount_path']


@app.route('/build_server')
def buildEnvironment(ip, username, password, service_name):


    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(ip, username=username, password=password,sock=None)
    
    sftp = ssh.open_sftp()
    sftp.put('check_script.sh', '/home/' + username + '/check_script.sh')
    sftp.close()
    
    check_cmd = 'bash check_script.sh ' + username + ' ' + password + ' ' + mount_ip + ' ' + mount_path + ' ' + ip + ' ' + lb
    _, sout, serr = ssh.exec_command(check_cmd)
    print 'CHeck script Output:', sout.read()
    print 'Error in script:', serr.read()

    return
    nfs_cmd = 'echo "' + password + '" | sudo -S apt-get install nfs-common -y; echo "' + password + '" | sudo -S mkdir -p /nfs/home; echo "' + password + '" | sudo -S mount 10.2.129.145:/home/priyendu/ias /nfs/home'
    print nfs_cmd
    _, sout, serr = ssh.exec_command(nfs_cmd)
    print 'Output:', sout.read()
    print 'Error:', serr.read()
    return


    _, sout, serr = ssh.exec_command('ps aux | grep server_stats.py')
    #print sout.read().decode() 

    if sout.read().decode().count('server_stats.py') == 3:
        #_, sout, serr = ssh.exec_command('pkill -f server_stats.py > /dev/null 2>&1')
        print 'Server stats already running'
        #print 'Killed server starts.py'
    else:    
        transport = ssh.get_transport()
        channel = transport.open_session()
        cmd_to_execute='python /media/bhavin/New\ Volume1/mtech/sem2/IAS/hackathon/hackathon2/ServerStatsModule/server_stats.py > /dev/null 2>&1 localhost &'
        channel.exec_command(cmd_to_execute)
        print 'Started server stats.py'
    _, sout, serr = ssh.exec_command('ps aux | grep start_docker_service.py')
    if sout.read().decode().count('start_docker_service.py') == 3:
        #_, sout, serr = ssh.exec_command('pkill -f start_docker_service.py > /dev/null 2>&1')
        print 'Start docker already running'
        #print 'Killed start docker service.py '
    else:
        print 'Starting start docker service.py'
        transport = ssh.get_transport()
        channel = transport.open_session()
        cmd_to_execute = 'bash /media/bhavin/New\ Volume1/mtech/sem2/IAS/hackathon/hackathon2/MachineAgent/start.sh'
        channel.exec_command(cmd_to_execute)
        time.sleep(3)
        print 'Started machine agent'
        print channel.recv(500)
        time.sleep(5)
    

        #print ssh_stdin
        #print stdout
        #result = stdout.read()
        #result1 = result.decode()
        #print result1
        #print stderr.read().decode()
        #print ssh_stderr
    
    return "Environment is ready"
@app.route('/release_server')
def ReleaseServer(ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(ip, username=username, password=password,sock=None)
    
    sftp = ssh.open_sftp()
    sftp.put('release.sh', '/home/' + username + '/release.sh')
    sftp.close()
    
    check_cmd = 'bash release.sh ' + username + ' ' + password + ' ' + mount_ip + ' ' + mount_path + ' ' + ip + ' ' + lb
    _, sout, serr = ssh.exec_command(check_cmd)
    return sout
    



def startService(ip, service_name):
    try:
        if requests.get('http://' + ip + ':8899/health').status_code == 200:
            print 'Starting my service'
            print requests.get('http://' + ip + ':8899/start_service/'+ service_name)
            
        else:
            print 'Not running'
    except Exception as e:
        print 'Exception occured:', e
        return str(e) + ' Start service docker failed'
def stopService(ip, service_name):
    try:
        if requests.get('http://' + ip + ':8899/health').status_code == 200:
            print 'Starting my service'
            print requests.get('http://' + ip + ':8899/start_service/'+ service_name)
            
        else:
            print 'Not running'
    except Exception as e:
        print 'Exception occured:', e
        return str(e) + ' Start service docker failed'

args = sys.argv

ip = args[1] # Host IP
username = args[1]
password = args[3]
lb = args[4] #Load balancer url
buildEnvironment(args[1], args[2], args[3], 'MyService')
#startService()

if __name__ == '__main__':
    print 'START SERVER MANAGER'
    app.run(debug=False, host='0.0.0.0',port=50022)