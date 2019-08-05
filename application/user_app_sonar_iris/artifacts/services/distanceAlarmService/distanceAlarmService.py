from flask import Flask, request, render_template
import pika
import time
import signal   
import random as random
import json
import requests
import socket
import sys
app = Flask(__name__)

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))


ip=s.getsockname()[0]
print(ip)   
loadBalancerIp=sys.argv[1]
loadBalancerIp=loadBalancerIp[7:]
RMQ_hostname=sys.argv[2]
# loadBalancerIp="192.168.43.54:5003"
####################################################
URL = "http://"+loadBalancerIp+"/get_service_ip/notificationService"
response=requests.get(url=URL)
loaddata = response.json()

ip_not = loaddata['ip']
port = loaddata['port']
deploy_soc=ip_not+":"+str(port)

###################################################
port="40004"
serviceName = "distanceAlarmService"
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



json_load=None
result_list=[]
node = pika.URLParameters("amqp://admin:admin@"+RMQ_hostname+":5672/%2F")
connection = pika.BlockingConnection(node)
channel = connection.channel()


def callback(ch, method, properties, body):
        print("Received Data"+str(body))

        json_load = json.loads(body)
        print ("Data : "+str(json_load['data']))
        channel.basic_ack(delivery_tag = method.delivery_tag)
        value = json_load['data']
        message = ""
        value=120
        if value > 0 and value < 100:
            message = "Emergency Stop " + str(value)
            #Message to list of people
        elif value > 101 and value < 200:
            message = "Critical " + str(value)
            URL="http://"+deploy_soc+"/notificationService"
            # print("Caller function called")
            r=requests.post(url=URL,data=json.dumps(message))
        else:
            message = "All Fine " + str(value)
        print(message)
        result_list.append(message)


@app.route('/getResult', methods=['GET','POST'])

def getResult():
    return jsonify(result_list)

@app.route('/distanceAlarmService')
def distanceAlarmService():
    # credentials = pika.PlainCredentials('guest', 'guest')
    # connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.43.48',5672,'/',credentials))
    # node = pika.URLParameters('amqp://admin:admin@192.168.43.48:5672/%2F')
    # connection = pika.BlockingConnection(node)
    # channel = connection.channel()

    channel.queue_declare(queue='DISTANCE', durable=True)

    

    channel.basic_consume(queue='DISTANCE',
                          auto_ack=False,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    



    

    
    # return render_template('index.html',message=message)

register(ip,port,serviceName,sdURL)

distanceAlarmService()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=40004, debug=False)
