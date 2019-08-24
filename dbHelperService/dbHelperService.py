from flask import Flask, request, render_template
import os
import json
from threading import Thread
from time import sleep
import time
import requests
import datetime
from Logger import Logger
import logging
import signal
import socket
import sys

app = Flask(__name__)


ip=sys.argv[3]
port = "49900"
serviceName = "dbHelperService"
sdURL = sys.argv[1]
############################################################
URL = sdURL+"/get_service_ip/dbService"
response=requests.get(url=URL)
loaddata = response.json()

ip_db = loaddata['ip']
port_db = loaddata['port']
db_soc=ip_db+":"+str(port_db)
############################################################

def handler(signal, frame):
	global ip, port, serviceName, sdURL
	print('CTRL-C pressed!')
	unregister(ip, port, serviceName, sdURL)
	sys.exit(0)


signal.signal(signal.SIGINT, handler)


def unregister(ip, port, serviceName, sdURL):
	print('Inside UnRegister')

	data = {"serviceName": serviceName, "IP": ip, "PORT": port}
	url = sdURL + '/unregister_service'
	print(url)
	print('Response:', requests.post(url, json=data))


def register(ip, port, serviceName, sdURL):
	print('Inside register')

	data = {"serviceName": serviceName, "IP": ip, "PORT": port}
	print('Response:', requests.post(sdURL + '/register_service', json=data))

@app.route('/health')
def health():
    return "OK"


@app.route('/modelListApp', methods=['GET', 'POST'])
def modelListApp():
	query = "select * from model where status=\"YES\""
	r=requests.post(url="http://"+db_soc+"/db_interaction",data=query)
	data = r.json()
	listOfModels=data
	data1={}
	data1['model']=[]
	for i in listOfModels:
		modelId=i[0]
		query="select deploy_socket,deploy_loc from schedule where model_id="+str(modelId)
		r=requests.post(url="http://"+db_soc+"/db_interaction",data=query)
		data = r.json()
		url1="http://"+data[0][0]+"/"+i[3]+""
		data1['model'].append({  
    	'name': i[1],
    	'url': url1,
		'gatewayLocation':data[0][1]
		})
	model_list = json.dumps(data1)
	return model_list


@app.route('/modelDown', methods=['GET', 'POST'])
def modelDown():
	data = request.data
	datadict = json.loads(data)
	modelName = datadict['modelName']
	print("--------------",modelName)
	query = "update model set status=\"Abnormal\" where model_name='"+modelName+"'"
	r=requests.post(url="http://"+db_soc+"/db_interaction",data=query)

@app.route('/get_service_details/<serviceName>', methods=['GET', 'POST'])
def get_service_details(serviceName):
	query = "select * from services where service_name='"+serviceName+"'"
	r=requests.post(url="http://"+db_soc+"/db_interaction",data=query)
	data = r.json()
	data = data[0]
	dictdata = {'serviceName':data[1],'highmark':data[5],'lowmark':data[6],'mininstance':data[4],'maxinstance':data[9],'minResponseTime':data[7]}
	return json.dumps(dictdata)


register(ip,port,serviceName,sdURL)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=49900, debug=False, threaded=True)