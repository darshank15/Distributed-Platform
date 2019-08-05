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
value=""
loadBalancerIp=sys.argv[1]
loadBalancerIp=loadBalancerIp[7:]
RMQ_hostname=sys.argv[2]
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))

app = Flask(__name__)

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))
ip=s.getsockname()[0]
# print(ip)   
# ip=s.getsockname()[0]
# print(ip)   
port="40080"
json_load=None
result_list=[]
node = pika.URLParameters("amqp://admin:admin@"+RMQ_hostname+":5672/%2F")

a="max"
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

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/push_data_to_RMQ', methods=['POST','GET'])
def push_data_to_RMQ():
    '''
    Supported Sensor Types: DISTANCE, SONAR, IRIS, DEFAULT
    
    RabbitMQ Queue Names : DISTANCE, SONAR, IRIS, DEFAULT
    '''
    #credentials = pika.PlainCredentials('guest', 'guest')
    #parameters = pika.ConnectionParameters('rabbit-server1', 5672, '/', credentials)
    global RMQ_hostname
    first = request.form['command']
    print(first)
    rmqhost=RMQ_hostname
    rmqqueue="DISTANCECOMMAND"
    # time.sleep(5)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmqhost))

    channel = connection.channel()  

    channel.queue_declare(queue=rmqqueue, durable=True)

    # time.sleep(1)
    # print("enter the input")
    # a=input()
    # sensor_data = generate_command_data()
    
    input1 = {"data":first}
    json_input = json.dumps(input1)
    channel.basic_publish(exchange='', routing_key=rmqqueue, body=json_input)

    print("Data Sent..")
    connection.close()
    return render_template('index.html')

# def producer():
#     try:
#         while(True):
#             push_data_to_RMQ(rmqhost=RMQ_hostname, rmqqueue="DISTANCECOMMAND")
#     except KeyboardInterrupt as identifier:
#         print("Sensor Stopped by User")


def callback1(ch, method, properties, body):
        global value
        # print("ddddd")
        json_load = json.loads(body)
        print ("Data of callback : "+str(json_load['data']))
        # channel.basic_ack(delivery_tag = method.delivery_tag)

        value = json_load['data']
        print("output: ",value)


     
@app.route('/get_command_data')
def get_command_data():
  # data = request.data
  global value
  # print(data)
  # result=json.loads(data)
  # print("ccc")
  dict1={}
  # print("dddddddddd",text)
  dict1["count"]=value
  # print("value ",value)
  return json.dumps(dict1)

def consumer1():
    global node
    #simultaneously consume from two queue
    connection = pika.BlockingConnection(node)
    channel = connection.channel()
    channel.queue_declare(queue='DISTANCEOUTPUT', durable=True)

    # args={'channel':channel}

    channel.basic_consume(queue='DISTANCEOUTPUT',
                          auto_ack=True,
                          on_message_callback=callback1)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()



# time.sleep(10)
# t3=Thread(target=consumer)
# t3.start()
serviceName="twowaySensorService"
register(ip,port,serviceName,sdURL)

# t1=Thread(target=push_data_to_RMQ)
# t1.start()
t2=Thread(target=consumer1)
t2.start()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=40080, debug=False, threaded=True)
