from flask import Flask, request, render_template
from werkzeug import secure_filename
import os
import json
import schedule
from threading import Thread
from time import sleep
import time
import requests
import datetime
from Logger import Logger
import logging
import signal
import smtplib
import ssl
import socket
import sys

app = Flask(__name__)

ip=sys.argv[3]
rabbitIp = sys.argv[2]
port = "49000"
serviceName = "scheduleService"
sdURL = sys.argv[1]


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


###################################################
# logger = Logger("amqp://admin:admin@"+rabbitIp+"//")
# my_logger = logging.getLogger('test_logger')
# my_logger.setLevel(logging.DEBUG)

# # rabbitmq handler
# logHandler = Logger("amqp://admin:admin@"+rabbitIp+"//")

# # adding rabbitmq handler
# my_logger.addHandler(logHandler)
################################################

c = 0
fg = 0

response=requests.get(url=sdURL+"/get_service_ip/dbService")
loaddata = response.json()
ipd = loaddata['ip']
portd = loaddata['port']
URLd = "http://"+ipd+":"+str(portd)+"/db_interaction"


def send(filename, modelname, port, ip, uname, passw, inp_str_ip):
	print("Run Model")
	start_script = "/home/" + uname + "/nfs/start_"+modelname+".sh"
	cmd3 = "nohup sshpass -p " + passw + " ssh -o StrictHostKeyChecking=no " + \
		ip + " -l " + uname + " bash " + start_script + " &"
	print(cmd3)
	os.system(cmd3)
	query="update model set status=\"YES\" where model_name='"+modelname+"'"
	r = requests.post(url=URLd, data=query)

	# if modelname == "my_model":
	# 	url = "http://"+ip+":"+str(port)+"/v1/models/"+modelname+":predict"
	# else:
	# 	url = "http://"+ip+":"+str(port)+"/v1/models/" + \
	# 							   modelname+"/versions/1"+":predict"
	# output_path = "./nfs/output_"+modelname+".txt"
	# cmd4 = "python3 ./nfs/process.py " + filename + " " + \
	# 	inp_str_ip + " " + url + " "+output_path+" &"
	# os.system(cmd4)
	
	
def endFunction(modelname,modelId,starttag, endtag, repeat, passw, ip, uname):
	print("End Model")
	end_script = "/home/" + uname + "/nfs/stop_"+modelname+".sh"
	endcmd = "nohup sshpass -p " + passw + " ssh -o StrictHostKeyChecking=no " + \
		ip + " -l " + uname + " bash " + end_script + " &"
	os.system(endcmd)
	query="update model set status=\"NO\" where model_name='"+modelname+"'"
	r = requests.post(url=URLd, data=query)
	query = "select model_id from model where model_name='"+modelName+"'"
	r = requests.post(url=URLd, data=query)
	data = r.json()
	mid = data[0][0]
	query="delete from schedule where model_id="+str(mid)
	r = requests.post(url=URLd, data=query)
	if repeat == "NO":
		schedule.clear(starttag)
		schedule.clear(endtag)

@app.route('/health')
def health():
    return "OK"

@app.route('/ScheduleService', methods=['GET', 'POST'])
def ScheduleService():
	print("Schedule")
	# my_logger.debug('Scheduler Service \t Start Scheduler')
	listOfDict = {}
	port = 45098
	global c
	global fg
	data = request.data
	datadict = json.loads(data)
	modelName = datadict['modelName']
	query="select model_id,status from model where model_name='"+modelName+"'"
	# query = "select model_id from model where model_name='"+modelName"+'"
	r = requests.post(url=URLd, data=query)
	data = r.json()
	print(data)
	modelId = data[0][0]
	status=data[0][1]
	stream_ip = ""
	start =""
	end = ""
	count = ""
	repeat = ""
	interval = ""
	repeat_period = ""
	ip = ""
	port = ""
	if status=="NO":
		query = "select start_time,end_time,interval_,count_,repeat_,repeat_period,deploy_socket,deploy_loc,uname,password from schedule where model_id="+str(modelId)
		r = requests.post(url=URLd, data=query)
		print(type(r))
		print(r)
		data = r.json()
		print(data)
		i = data
		print(i)
		start = i[0][0]
		end = i[0][1]
		count = i[0][3]
		repeat = i[0][4]
		interval = i[0][2]
		repeat_period = i[0][5]
		deploy_socket=i[0][6]
		deploy_loc = i[0][7]
		ip_port=deploy_socket.split(':')
		ip = ip_port[0]
		port = ip_port[1]
		if deploy_loc == "Gateway":
			query="select uname,password from gateway where ip='"+ip+"'"
			r=requests.post(url=URLd,data=query)
			data = r.json()
			uname = data[0][0]
			password = data[0][1] 
		else:
			uname = data[0][8]
			password = data[0][9]
	else:
		
		# url='http://192.168.43.225/request_manager'
		# response = requests.post(url,data=r)
		query = "select interval_,count_,repeat_,repeat_period,deploy_socket,deploy_loc,uname,password from schedule where model_id="+str(modelId)
		r = requests.post(url=URLd, data=query)
		data = r.json()
		i = data
		start = "NA"
		end = "NA"
		count = i[0][1]
		repeat = i[0][2]
		interval = i[0][0]
		repeat_period = i[0][3]
		deploy_socket=i[0][4]
		deploy_loc = i[0][5]
		ip_port=deploy_socket.split(':')
		ip = ip_port[0]
		port = ip_port[1]
		if deploy_loc == "Gateway":
			query="select uname,password from gateway where ip='"+ip+"'"
			r=requests.post(url=URLd,data=query)
			data = r.json()
			uname = data[0][0]
			password = data[0][1] 
		else:
			uname = data[0][6]
			password = data[0][7]
	##################################################
	


	if fg == 0:
		fg = 1
		once()

	starttag = "tag"+str(c)
	c = c + 1
	endtag = "tag"+str(c)
	# print("---------------------@@@@@@@@@@@@@@@@@@@@@")
	if end != "NA" and repeat == "YES":
		schedule.every().day.at(start).do(send, filename=modelName, modelname=modelName, port=port, ip=ip,
													uname=uname, passw=password,inp_str_ip=stream_ip).tag(starttag)
		schedule.every().day.at(end).do(endFunction, modelname=modelName,modelId=modelId,
												starttag=starttag, endtag=endtag, repeat=repeat, passw=password, ip=ip, uname=uname).tag(endtag)
	elif end != "NA" and repeat == "NO":
		schedule.every().day.at(start).do(send, filename=modelName, modelname=modelName, port=port, ip=ip, uname=uname, passw=password, inp_str_ip=stream_ip).tag(starttag)
		schedule.every().day.at(end).do(endFunction, modelname=modelName,modelId=modelId,
											starttag=starttag, endtag=endtag, repeat=repeat, passw=password, ip=ip, uname=uname).tag(endtag)
	elif start == "NA" and end == "NA" and count == 1:
		now = datetime.datetime.now()
		start_hour = ""
		start_minute = ""
		end_hour = ""
		end_minute = ""

		if now.hour < 10:
			start_hour = "0" + str(now.hour)
		else:
			start_hour = str(now.hour)
		if now.minute + 1 < 10:
			start_minute = "0" + str(now.minute+1)
		else:
			start_minute = str(now.minute+1)

		start = start_hour + ":" + start_minute
		end = now + datetime.timedelta(minutes=int(data['interval']+1))

		if end.hour < 10:
			end_hour = "0" + str(end.hour)
		else:
			end_hour = str(end.hour)
		if end.minute < 10:
			end_minute = "0" + str(end.minute)
		else:
			end_minute = str(end.minute)
		end = end_hour + ":" + end_minute
		print(start, end)
		schedule.every().day.at(start).do(send, filename=modelName, modelname=modelName, port=port, ip=ip, uname=uname, passw=password,inp_str_ip=stream_ip).tag(starttag)
		schedule.every().day.at(end).do(endFunction,
										modelname=modelName,modelId=modelId, starttag=starttag, endtag=endtag, repeat=repeat, passw=password, ip=ip, uname=uname).tag(endtag)
	else:
		for j in range(count):
			if j == 0:
				now = datetime.datetime.now()
			start_hour = ""
			start_minute = ""
			end_hour = ""
			end_minute = ""
			if now.hour < 10:
				start_hour = "0" + str(now.hour)
			else:
				start_hour = str(now.hour)
			if now.minute + 1 < 10:
				start_minute = "0" + str(now.minute+1)
			else:
				start_minute = str(now.minute+1)
			start = start_hour + ":" + start_minute
			end = now + datetime.timedelta(minutes=int(interval+1))
			if end.hour < 10:
				end_hour = "0" + str(end.hour)
			else:
				end_hour = str(end.hour)
			if end.minute < 10:
				end_minute = "0" + str(end.minute)
			else:
				end_minute = str(end.minute)

			end = end_hour + ":" + end_minute
			print(start, end)
			schedule.every().day.at(start).do(send, filename=modelName, modelname=modelName, port=port, ip=ip, uname=uname, passw=password,inp_str_ip=stream_ip).tag(starttag)
			schedule.every().day.at(end).do(endFunction,
											modelname=modelName,modelId=modelId, starttag=starttag, endtag=endtag, repeat=repeat, passw=password, ip=ip, uname=uname).tag(endtag)
			now = now + \
				datetime.timedelta(minutes=int(repeat_period))
	c = c + 1
	# my_logger.debug('Scheduler Service \t Done Scheduler')
	return "From Schedule"


def once():
	thread = Thread(target=threaded_function)
	thread.start()


def threaded_function():
	while True:
		schedule.run_pending()
		time.sleep(1)


register(ip,port,serviceName,sdURL)

if __name__ == '__main__':
	app.run(host="0.0.0.0",port=49000, debug=False,threaded=True)
