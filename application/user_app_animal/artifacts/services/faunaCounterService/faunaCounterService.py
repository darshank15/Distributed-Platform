from flask import Flask, request, render_template
import pika
import time
import signal   
import random as random
import json
import requests
import base64
import socket
import sys
from prediction_client import *
from threading import Thread
import numpy as np
from cv2 import *

app = Flask(__name__)

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))


ip=s.getsockname()[0]
print(ip)   

loadBalancerIp= sys.argv[1]
rabbitMQIP = sys.argv[2]
print("******************************** LOAD BALANCER IP : ", loadBalancerIp )

print("******************************** RBMQ IP : ", rabbitMQIP )

###################################################
port="50006"
serviceName = "faunaCounterService"
sdURL = loadBalancerIp
######################################################
URL = loadBalancerIp+"/get_service_ip/dbHelperService"
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
#print(loaddata)
for model_dict in loaddata['model']:
    if model_dict['name']=='animalWelfare':
        model_url=model_dict['url']

print("******************************** model url : ", model_url )
# it should be like : 'http://localhost:8501/v1/models/resnet:predict'

######################################################

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
label_dict = dict()
with open('./label.json') as f:
    label_dict = json.load(f)
################################
print("******************************** DICT done " )


result_list=[]
json_load=None
node = pika.URLParameters('amqp://admin:admin@'+rabbitMQIP+':5672/%2F')
connection = pika.BlockingConnection(node)
channel = connection.channel()
classlist = ["elephant","lion","leopard"]
final_class={}
for i in classlist:
   final_class[i]=0

def callback(ch, method, properties, body):

    # print("Received Data"+str(body))

    json_load = json.loads(body)
    channel.basic_ack(delivery_tag = method.delivery_tag)
    # mapping = {"0":"elephant","1":"lion","2":"leopard"}
    a_restored = np.asarray(json_load["img"])
    #print(a_restored)
    print(a_restored.shape)
    print("image received")

    my_int = random.randint(0, 10000)
    index = str(my_int)
    #pygame.image.save(body,"received_"+index+".jpg")
    imwrite("received_"+index+".jpg",a_restored)
    """
        NOT SURE FOR LOCAL IMAGES.
    """
    IMAGE_URL="./received_"+ index +".jpg"
    SERVER_URL = model_url+":predict"#check this guy
    #print("******************************** Pred url ", SERVER_URL )
    print("We are done")
    f = open(IMAGE_URL, 'rb')
    img = f.read()
    prediction = main(img,SERVER_URL)

    # dl_request = requests.get(IMAGE_URL, stream=True)
    # dl_request.raise_for_status()

    # # Compose a JSON Predict request (send JPEG image in base64).
    # jpeg_bytes = base64.b64encode(dl_request.content).decode('utf-8')
    # predict_request = '{"instances" : [{"b64": "%s"}]}' % jpeg_bytes

    # Send few requests to warm-up the model.
    # for _ in range(3):
    #     response = requests.post(SERVER_URL, data=predict_request)
    #     response.raise_for_status()

    # Send few actual requests and report average latency.
    
    # response = requests.post(SERVER_URL, data=predict_request)
    # response.raise_for_status()
    # prediction = response.json()['predictions'][0]
    
    print('Prediction class: {}'.format(prediction['classes']))
    out_label = label_dict[str(prediction['classes'])]

    for label in classlist:
        if out_label in label:
            final_class[out_label] += 1
            break
    print("******************************** DICT ", final_class )

def start_consume():
    channel.queue_declare(queue='CAMERA', durable=True)



    channel.basic_consume(queue='CAMERA',
                          auto_ack=False,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


@app.route('/faunaCounterService')
def faunaCounterService():
    t1 = Thread(target=start_consume)
    t1.start()
   
   
@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_helper_data')
def get_helper_data():
    result={}
    countlist2=[]
    for value in final_class.values():
      countlist2.append(value)
    print("###############################")
    print(countlist2)
    classlist2 = ['elephant','lion','leopard']
    #return render_template('index.html',graph = mapping,classlist=classlist2,countlist=countlist2)
    # result = {}
    result['labels'] = classlist2
    result['values'] = countlist2
    return json.dumps(result)


register(ip,port,serviceName,sdURL)

faunaCounterService()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=50006, debug=True)
