from flask import Flask, request, render_template
import pika
import time
import random as random
import json
import signal
import requests
import smtplib, ssl
import sys
import socket
app = Flask(__name__)

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.connect(('8.8.8.8',1))
loadBalancerIp=sys.argv[1]
loadBalancerIp=loadBalancerIp[7:]
RMQ_hostname=sys.argv[2]

ip=s.getsockname()[0]
print(ip)   

###########################
# ip="192.168.43.110"
port="42008"
serviceName = "notificationService"
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

###########################
@app.route('/notificationService',methods=['POST'])
def notificationService():
	data = request.data
	msg=json.loads(data)
	# message=
	print(msg)
	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	sender_email = "johan.stark95@gmail.com"  # Enter your address
	receiver_email = "kansagara.darshan97@gmail.com"  # Enter receiver address
	password = "1friend1"
	message = "Subject: "+msg

	
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
	    server.login(sender_email, password)
	    server.sendmail(sender_email, receiver_email, message)

register(ip,port,serviceName,sdURL)
# notificationService()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=42008, debug=False, threaded=True)