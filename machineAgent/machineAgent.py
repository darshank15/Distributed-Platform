import json
from flask import Flask,request
import sys
import socket
import os
import time
import xmltodict


app = Flask(__name__)
args = sys.argv
sd_url = args[1]
rmq_ip = args[2]
my_ip = args[3]
pwd = args[4]

counter = 0

def get_pids(name):
	output = []
	cmd = "ps -aef | grep -i '%s' | grep -v 'grep' | awk '{ print $2 }' > /tmp/out"
	os.system(cmd % name)
	with open('/tmp/out', 'r') as f:
		line = f.readline()
		while line:
			output.append(line.strip())
			line = f.readline()
			if line.strip():
				output.append(line.strip())

	return list(set(output))


def get_free_tcp_port():
	tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	tcp.bind(('', 0))
	addr, port = tcp.getsockname()
	tcp.close()
	return port

@app.route('/health')
def health():
	global counter
	counter += 1
	return str(counter)

def checkServiceType(service_name):
	system_services = []
	home = os.path.expanduser("~")
	path = home+"/nfs/platform_config.xml"
	
	with open(path) as fd:
		doc = xmltodict.parse(fd.read())

	d = doc['main']['services']['service']
	d = json.dumps(d)
	services = json.loads(d)

	for service in services:
		system_services.append(service['serviceName'])

	
	if service_name in system_services:
		return "system"
	else:
		return "user"

@app.route('/start_service/<service_name>')
def start_service(service_name): 
	global counter
	counter += 1

	try:
		service_type = checkServiceType(service_name)
		home = os.path.expanduser("~")
		if service_type == "user":	
			path = home+"/nfs/user_app/artifacts/services/"
			path += service_name+".zip"

			if not os.path.exists(home+"/temp"):
				os.makedirs(home+"/temp")

			cur_path = os.path.abspath(os.curdir)

			if not os.path.exists(home+"/temp/"+service_name+".zip"):
				print "afs"
				os.system("cp "+path+" "+home+"/temp")

				os.chdir(home+"/temp")
				os.system("unzip "+service_name+".zip" )
				os.chdir(service_name)
			else:
				os.chdir(home+"/temp")
				
				os.chdir(service_name)

			os.system("nohup bash start.sh "+sd_url+" "+rmq_ip+" "+my_ip+" "+pwd+" &")
			print "running ",service_name

			os.chdir(cur_path)

		else:
			path = home+"/nfs/SystemServices/"
			path += service_name+".zip"

			if not os.path.exists(home+"/temp"):
				os.makedirs(home+"/temp")

			cur_path = os.path.abspath(os.curdir)

			if not os.path.exists(home+"/temp/"+service_name+".zip"):
				os.system("cp "+path+" "+home+"/temp")

				os.chdir(home+"/temp")
				os.system("unzip "+service_name+".zip" )
				os.chdir(service_name)
			else:
				os.chdir(home+"/temp")
				
				os.chdir(service_name)

			os.system("nohup bash start.sh "+sd_url+" "+rmq_ip+" "+my_ip+" "+pwd+" &")
			print "running ",service_name
			os.chdir(cur_path)

		time.sleep(2)
		return str(service_name+" started")

	except Exception as e:
		return 'Exception: '+e

@app.route('/stop_service/<service_name>')
def stop_service(service_name):
	try:
		pids = get_pids(service_name)
		# for pid in pids:
		# 	print "killing ",pid
		os.kill(int(pids[0]),9)

		return service_name+" killed"
	except Exception as e:
		print e
		return "Couldn't kill "+service_name

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=8899,debug=False,threaded=True)
