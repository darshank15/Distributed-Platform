from flask import Flask, request, render_template
import pika
import time
import signal
import random as random
import json
import requests
import socket
from threading import Thread
import sys

app = Flask(__name__)

# s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# s.connect(('8.8.8.8',1))
# ip=s.getsockname()[0]
# print(ip)   
ip=sys.argv[3]
loadBalancerIp=sys.argv[1]
loadBalancerIp=loadBalancerIp[7:]
RMQ_hostname=sys.argv[2]
##########################################
URL = "http://"+loadBalancerIp+"/get_service_ip/dbHelperService"
response=requests.get(url=URL)
loaddata = response.json()

ip_db = loaddata['ip']
port_db = loaddata['port']
deploy_soc=ip_db+":"+str(port_db)
URL = "http://"+deploy_soc+"/modelListApp"
response=requests.post(url=URL)
loaddata = response.json()
model_url=""
for model_dict in loaddata['model']:
    if model_dict['name']=='iris':
        model_url=model_dict['url']
###########################################
port="40005"
serviceName = "helperService"
# sdURL = "http://"+loadBalancerIp
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
################################

result_list=[]
json_load=None
node = pika.URLParameters("amqp://admin:admin@"+RMQ_hostname+":5672/%2F")
connection = pika.BlockingConnection(node)
channel = connection.channel()
classlist = ["Iris_Sentosa","Iris_versicolor","Iris_virginica"]
final_class={}
for i in classlist:
   final_class[i]=0

def callback(ch, method, properties, body):
         print("Received Data"+str(body))

         json_load = json.loads(body)
         print(type(json_load))
         print ("Data : "+str(json_load['data']))
         channel.basic_ack(delivery_tag = method.delivery_tag)
         mapping = {"0":"Iris_Sentosa","1":"Iris_versicolor","2":"Iris_virginica"}
         
         # listOfDict = json.load(json_file)
         data={}
         data['signature_name']="predict"
         data['instances']=[]
         data1={}
         data1['sepal_length']=[]
         data1['sepal_width']=[]
         data1['petal_length']=[]
         data1['petal_width']=[]
         data1['sepal_length'].append(json_load['data'][0])
         data1['sepal_width'].append(json_load['data'][1])
         data1['petal_length'].append(json_load['data'][2])
         data1['petal_width'].append(json_load['data'][3])
         data['instances'].append(data1)
         print("data",data)
         # url = "http://192.168.43.110:8901/v1/models/my_model1/versions/1:predict"
         url = model_url+":predict"

         response=requests.post(url,data=json.dumps(data))
         data = response.json()
         result = data
         print("result",result)
         temp=result['predictions'][0]['class_ids'][0]
         print("temp ",temp)
         i1=mapping[str(temp)]
         final_class[i1]=final_class[i1]+1
         print(final_class) 

def start_consume():
    channel.queue_declare(queue='IRIS', durable=True)



    channel.basic_consume(queue='IRIS',
                          auto_ack=False,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


@app.route('/helperService')
def helperService():
    t1 = Thread(target=start_consume)
    t1.start()
   
   
@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_helper_data')
def get_helper_data():
    # print(dict1)
    # print(type(dict1))
    result={}
    countlist2=[]
    for value in final_class.values():
      countlist2.append(value)
    print("###############################")
    print(countlist2)
    classlist2 = ['Iris_Sentosa','Iris_versicolor','Iris_virginica']
    #return render_template('index.html',graph = mapping,classlist=classlist2,countlist=countlist2)
    # result = {}
    result['labels'] = classlist2
    result['values'] = countlist2
    return json.dumps(result) 




register(ip,port,serviceName,sdURL)
helperService()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=40005, debug=False, threaded=True)
