from flask import Flask, request, render_template
import flask
import signal
import pika
import time
import random as random
import json
import signal
import requests
import smtplib, ssl
import numpy as np
import socket
from threading import Thread
import sys


app = Flask(__name__)
loadBalancerIp=sys.argv[1]
loadBalancerIp=loadBalancerIp[7:]
RMQ_hostname=sys.argv[2]
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))
ip=s.getsockname()[0]
# loadBalancerIp="192.168.43.54:5003"
#################################################################
print(loadBalancerIp)
URL = "http://"+loadBalancerIp+"/get_service_ip/dbHelperService"
response=requests.get(url=URL)
loaddata = response.json()
print(loaddata)
ip_db = loaddata['ip']
port_db = loaddata['port']
deploy_soc=ip_db+":"+str(port_db)
URL = "http://"+deploy_soc+"/modelListApp"
response=requests.post(url=URL)
loaddata = response.json()
model_url=""
for model_dict in loaddata['model']:
	if model_dict['name']=='Sonar':
		model_url=model_dict['url']

# URL = "http://"+loadBalancerIp+"/get_service_ip/notificationService"
# response=requests.get(url=URL)
# loaddata = response.json()
# ip_not = loaddata['ip']
# port_not = loaddata['port']
# deploy_soc=ip_not+":"+str(port_not)
###################################################################

# print(ip)   
port="40012"
serviceName = "counterService"
sdURL = "http://"+loadBalancerIp



def handler(signal, frame):
    global ip, port, serviceName, sdURL
    print('CTRL-C pressed!')
    unregister(ip, port, serviceName, sdURL)
    sys.exit(0)

signal.signal(signal.SIGINT, handler)

def unregister(ip, port, serviceName, sdURL):
    print('Inside UnRegister')

    data = {"serviceName":serviceName, "IP":ip, "PORT":port }
    url = sdURL + '/unregister_service'
    print(url)
    print('Response:', requests.post(url, json=data))


def register(ip, port, serviceName, sdURL):
    print('Inside register')

    data = {"serviceName":serviceName, "IP":ip, "PORT":port }
    print('Response:', requests.post(sdURL + '/register_service', json=data))


@app.route('/health')
def health():
    return "OK"

message=""
json_load=None
result_list=[]
node = pika.URLParameters("amqp://admin:admin@"+RMQ_hostname+":5672/%2F")
connection = pika.BlockingConnection(node)
channel = connection.channel()
text=""
def callback(ch, method, properties, body):

        print("Received Data"+str(body))
        global text
        global message
        json_load = json.loads(body)
        print ("Data : "+str(json_load['data']))
        channel.basic_ack(delivery_tag = method.delivery_tag)
        # df = pd.read_csv('./Sonar.csv')

        # eval_data = df[df.columns[0:60]].values
        # eval_labels = df[df.columns[60]]

        Predictions_list = []
        data1=[]
        # for i in range(eval_data.shape[0]):
        eval_data=[0.0221, 0.0065, 0.0164, 0.0487, 0.0519, 0.0849, 0.0812, 0.1833, 0.2228, 0.181, 0.2549, 0.2984, 0.2624, 0.1893, 0.0668, 0.2666, 0.4274, 0.6291, 0.7782, 0.7686, 0.8099, 0.8493, 0.944, 0.945, 0.9655, 0.8045, 0.4969, 0.396, 0.3856, 0.5574, 0.7309, 0.8549, 0.9425, 0.8726, 0.6673, 0.4694, 0.1546, 0.1748, 0.3607, 0.5208, 0.5177, 0.3702, 0.224, 0.0816, 0.0395, 0.0785, 0.1052, 0.1034, 0.0764, 0.0216, 0.0167, 0.0089, 0.0051, 0.0015, 0.0075, 0.0058, 0.0016, 0.007, 0.0074, 0.0038]
        # data = json.dumps({"signature_name": "model", "instances":json_load['data']})
        data1.append(json_load['data'])
        data = json.dumps({"signature_name": "model", "instances":data1})

        print("data: ", data)



        headers = {"content-type":"application/json"}
        # json_response = requests.post('http://127.0.0.1:8900/v1/models/Sonar/versions/1:predict', data=data, headers=headers)
        json_response = requests.post(model_url+":predict", data=data, headers=headers)
        print (json_response.text)

        predictions = json.loads(json_response.text)["predictions"]

        predictions = np.array(predictions)
        ans=np.argmax(predictions, axis=1)
        print("ffffffff")
        print(ans[0])
        with open("file1.txt", "r+") as f:
	        text = f.readline()
	        print(type(text))
	        print(text)
	        f.seek(0)
	        res=int(text)+1
	        f.write(str(res))
	        f.truncate()
	        f.close()
        if ans[0]==1:
        	message="Mine"
        else:
          message="Rock"
          print("message ",message)

        # print("ans ",ans)
def call():
    channel.queue_declare(queue='SONAR', durable=True)



    channel.basic_consume(queue='SONAR',
                          auto_ack=False,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


@app.route('/counterService')
def CounterService():
    t1=Thread(target=call)
    t1.start()
    

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_counter_data')
def get_counter_data():
  # data = request.data
  global text
  # print(data)
  # result=json.loads(data)
  # print("ccc")
  dict1={}
  # print("dddddddddd",text)
  dict1["count"]=text
  return json.dumps(dict1)

@app.route('/indexMine')
def indexMine():
  return render_template('indexMine.html')



@app.route('/get_mine_data')
def get_mine_data():
  global message
  dict1={}
  print("msg ",message)
  dict1['message']=message
  return json.dumps(dict1)
	# return message

    
register(ip,port,serviceName,sdURL)
CounterService()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=40012, debug=False, threaded=True)

    