#!/usr/bin/env python
import pika
import random, os, time, json, sys
import numpy as np
import pandas as pd
from DistanceSensor import *
from IrisSensor import *
from SonarSensor import *
from threading import Thread

node = pika.URLParameters('amqp://admin:admin@localhost:5672/%2F')
sensor = ''
class NumpyEncoder(json.JSONEncoder):
    '''
    A Util class for Json#load and Json#dumps funtions
    '''
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def push_data_to_RMQ( sensor_type='DEFAULT', rmqhost="localhost", rmqqueue="hello"):
    '''
    Supported Sensor Types: DISTANCE, SONAR, IRIS, DEFAULT
    
    RabbitMQ Queue Names : DISTANCE, SONAR, IRIS, DEFAULT
    '''
    #credentials = pika.PlainCredentials('guest', 'guest')
    #parameters = pika.ConnectionParameters('rabbit-server1', 5672, '/', credentials)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmqhost))

    channel = connection.channel()

    channel.queue_declare(queue=rmqqueue, durable=True)
    global sensor
        #channel.queue_declare(queue="INPUT", durable=True)
    if sensor_type == 'DISTANCE':
        time.sleep(1)
        sensor_data = sensor.generateData()
        
        input = {"data":sensor_data}
        json_input = json.dumps(input)
        channel.basic_publish(exchange='', routing_key=rmqqueue, body=json_input)
        #channel.basic_publish(exchange='', routing_key="INPUT", body=json_input)

    elif(sensor_type == 'SONAR'):
        time.sleep(10)
        sensor_data = sensor.generateData()

        input = {"data":sensor_data}
        json_input = json.dumps(input, cls=NumpyEncoder)
        channel.basic_publish(exchange='', routing_key=rmqqueue, body=json_input)
    elif(sensor_type == 'IRIS'):
        time.sleep(0.5)
        sensor_data = sensor.generateData()

        input = {"data":sensor_data}
        json_input = json.dumps(input, cls=NumpyEncoder)
        channel.basic_publish(exchange='', routing_key=rmqqueue, body=json_input)
    else:
        pass

    print("Data Sent..")
    connection.close()

def to_output_file(distance):
    f = open("distance.txt", "w")
    f.write("Distance : "+str(distance))
    f.close()


def callback(ch, method, properties, body):
    # print("ddddddddddddddddd")
    global sensor
    global node
    # print('INSIDE CALLBACK')
    json_load = json.loads(body)
    # print (json_load)
    # print ('Args in callback:', sensor.getType() )
    output=sensor.executeCommand(json_load['data'])
    print("output")
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    
    channel1 = connection1.channel()  

    channel1.queue_declare(queue="DISTANCEOUTPUT", durable=True)

    time.sleep(1)
    input = {"data":output}
    json_input = json.dumps(input)
    channel1.basic_publish(exchange='', routing_key="DISTANCEOUTPUT", body=json_input)
    connection1.close()  

    # print("Data Sent..")
    


def commandListener():
    #simultaneously consume from two queue
    global node
    global sensor
    print("dddd")
    connection = pika.BlockingConnection(node)
    channel = connection.channel()
    channel.queue_declare(queue=sensor.getName() + 'COMMAND', durable=True)

    
    channel.basic_consume(queue=sensor.getName() + 'COMMAND',
                          auto_ack=True,
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print('Please provide RabbitMQ machine IP Address as first command line argument')
        sys.exit()
    if  len(sys.argv) < 3:
        print('Please provide 2nd argument as dataset type. Example : DISTANCE, SONAR, IRIS')
        sys.exit()

    RMQ_hostname = sys.argv[1]
    dataset_type = sys.argv[2]
    try:
        if dataset_type == 'IRIS':
            sensor = IrisSensor()
        if dataset_type == 'DISTANCE':
            sensor = DistanceSensor()
        if dataset_type == 'SONAR':
            sensor = SonarSensor()
        print( sensor.getType() )
        if sensor.getType() == "TWO_WAY":
            print("aaa")
            t = Thread(target = commandListener )
            t.start()
        while(True):
            push_data_to_RMQ(sensor_type=dataset_type, rmqhost=RMQ_hostname, rmqqueue=dataset_type)
    except KeyboardInterrupt as identifier:
        print("Sensor Stopped by User")
