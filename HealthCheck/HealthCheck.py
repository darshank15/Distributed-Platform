import subprocess
import json
import requests
import threading 
import sys
from Logger import Logger
import logging
import time 
import os
args = sys.argv
lb_URL = args[1]
rmq_host = args[2]
host_url = args[3]



get_all_URL = lb_URL + "/get_all_services"
get_models = "/modelListApp"

post_schedule = "/ScheduleService"

my_logger = logging.getLogger('test_logger')
my_logger.setLevel(logging.DEBUG)

logHandler = Logger(uri='amqp://admin:admin@' + rmq_host + '//', host_url=host_url)

# adding rabbitmq handler
my_logger.addHandler(logHandler)


#{"modelName":"iris"}
def check_model(model_url, model_name, service_url, location):
	#my_logger.debug('HealthCheckService \t check_model ' + model_url)

	try:
		res = requests.get(url = model_url) #ping models
		print 'Model is running:', model_url
	except Exception as e:
		data = {
			"modelName":model_name,
			"deploy_loc":location
		}
		print 'Model is DOWN', model_url
		print 'Before split:', service_url
		service_url = "/".join( service_url.split("/")[:-1] )
		print 'Service url for scheduling:', service_url + "/modelDown"
		requests.post(service_url + "/modelDown", data=json.dumps(data))
		if location != 'Gateway':
			print 'Location is GATEWAY'
			deployServiceURL = requests.get(lb_URL + "/get_service_ip/deployService").json()
			if 'IP' in deployServiceURL:

				deployServiceURL = deployServiceURL['IP'] + ':' + deployServiceURL['port']
				print 'Deploy service url:', deployServiceURL
				print requests.posts(deployServiceURL + '/deploy', data=json.dumps(data))

				print 'Deploy service invoked'
			else:
				'Deploy service not registered'
		
		print 'Data for model:', json.dumps(data)
		data = json.dumps(data)
		scheduleURL = requests.get(lb_URL + "/get_service_ip/scheduleService").json()
		if 'ip' in scheduleURL:

			scheduleURL = scheduleURL['ip'] + ':' + scheduleURL['port']
			print 'schedule service url:', scheduleURL
			print requests.post("http://" + scheduleURL + post_schedule, data=data)

			print 'scheduleURL service invoked'
		else:
			'scheduleURL service not registered'
		#print requests.post(service_url  + post_schedule, data=data)
		#print 'Schedule Service called to reschedule model:', service_url + post_schedule
def start_service(service_name, serviceIP):
	find_location_url = lb_URL + "/find_server_location/" + serviceIP
	r = requests.get(url = find_location_url).json()
	print 'R:', r

	if r == "Cloud":
		get_instance_URL = lb_URL + "/get_free_server"
		r = requests.get(url = get_instance_URL)
		server = r.json()['ip'] + ":8899"
	else:
		server = serviceIP + ":8899"
	print server
	#server = "localhost:8899"
	request_service_up_URL = "http://"+server+"/start_service/"+service_name
	print request_service_up_URL
	requests.get(url = request_service_up_URL)
	print 'Request sent to start service:', service_name

def check_health(service_url,service_name, data):
	#service_url+="/123"
	#my_logger.debug('HealthCheckService \t check_health ' + service_url)
	print service_url
	try:
		try:
			res = requests.get(url = service_url)
		except:
			time.sleep(10)
			res = requests.get(url = service_url)
		#my_logger.debug('HealthCheckService \t check_health service is UP:' + service_name)
		try:
			print 'Service is UP:', service_name
			#requests.get(lb_URL)
			db_helper_service_url = ''
			numberOfInstances = 0
			serviceIP = ":".join( service_url.split(":")[:-1] )
			serverLoad = ''
			for server in data['servers']:
				if server['ip'] == serviceIP:
					serverLoad = server['cpu']
					break


			for service in data['services']:
				if service['serviceName'] == 'dbHelperService':
					db_helper_service_url = service['instances'][0]
					numberOfInstances = len( service['instances'] )
					break
			if db_helper_service_url != '':

				response = requests.get('http://' + db_helper_service_url + '/get_service_details/' + service_name)
				response = response.json()
				#print 'Response:', response
				#print 'ServerLoad:', serverLoad
				minLoad = response['lowmark']
				maxLoad = response['highmark']
				minInstance = response['mininstance']
				maxInstance = response['maxinstance']

				if serverLoad > maxLoad and numberOfInstances < maxInstance:
					requests.get(lb_URL + "/get_free_server")
				else:
					print 'All OK'
				





			if service_name == "dbHelperService":
				service_url = service_url[:-7]
				service_url = service_url + get_models
				print 'Service url for models:', service_url
				models = requests.get(service_url).json()['model'] #Call InvocationService/get_models
				#{"model": [{"name": "iris", "url": "http://'192.168.43.110:9000'/'v1/my_model:predict'", "gatewayLocation": "Gateway"}, {"name": "naval-mine", "url": "http://'192.168.43.110:9000'/'v1/my_model1:predict'", "gatewayLocation": "Gateway"}]}
				for model in models:
					model_url = model['url']
					model_name = model['name']
					location = model['gatewayLocation']
					
					t1 = threading.Thread(target=check_model,args=((model_url, model_name, service_url, location)) )
					t1.start()
		except Exception as e:
			print e

	except:
		print 'Service is DOWN:', service_name
		#my_logger.debug('HealthCheckService \t check_health service is DOWN:' + service_name)
		service_url = service_url[7:]
		serviceIP, servicePORT = service_url.split(":")
		servicePORT = servicePORT.split('/')[0]
		unregister_data = {
			"IP":serviceIP,
			"PORT": servicePORT,
			"serviceName": service_name

		}
		requests.post(lb_URL + "/unregister_service", json=unregister_data)
		start_service(service_name, serviceIP)



def checkServiceHealth(data):
	for service in data['services']:
		instances = service['instances']
		service_name = service['serviceName']
		
		for instance in instances:
			service_url = "http://"+instance+"/health" 
			print service_url
			t1 = threading.Thread(target=check_health,args=((service_url,service_name, data)))
			t1.start()
def ping_servers(ip):
	FNULL = open(os.devnull, 'w')
	#retcode = subprocess.call(['echo', 'foo'], stdout=FNULL, stderr=subprocess.STDOUT)
	res = subprocess.call(['ping', '-w','5', '-c', '1', ip], stdout=FNULL, stderr=subprocess.STDOUT)
	status="True"
	if res == 0:
		print "ping to", ip, "OK"
	else:
		#print "NO RESPONSE from", ip
		status = "False"
	data = {
		"IP":ip,
		"status":status
	}
	my_logger.debug('HealthCheckService \t ping_servers' + str(data['IP']) )
	requests.post(lb_URL + '/update_server_status', json=data)
def checkServerHealth(data):
	for service in data['servers']:
		ip = service['ip']		
			
		
		t1 = threading.Thread(target=ping_servers,args=((ip,)))
		t1.start()

while True:
	try:

		r = requests.get(url = get_all_URL)
		data = r.json()
		#print data
		t1 = threading.Thread(target=checkServiceHealth,args=((data,)))
		t1.start()

		t2 = threading.Thread(target=checkServerHealth,args=((data,)))
		t2.start()
		
					
		time.sleep(10)
	except Exception as e:
		print 'Exception:', e
		#my_logger.debug()