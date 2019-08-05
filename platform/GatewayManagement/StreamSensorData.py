from kombu import Connection, Exchange, Producer, Queue
import time
import sys
import os
import random
from PIL import Image
import json
import numpy as np
argument_list = sys.argv
#queue_name = 'Device_1_text_stream'
mnist_data_path = 'hack2/our_test'
iris_path = 'iris/Iris.csv'
queue_list = { "mnist": "mnist-queue", "iris":"iris-queue"}
exchange_list = { "mnist": "exchange-mnist", "iris":"exchange-iris"}

type_of_model = argument_list[1]

url = argument_list[2]
rabbit_url = "amqp://admin:admin@" + url + ":5672/"

queue_name = queue_list[type_of_model]
exchange_name = exchange_list[type_of_model]

conn = Connection(rabbit_url)
channel = conn.channel()
exchange = Exchange(exchange_name, type="direct")
producer = Producer(exchange=exchange, channel=channel, routing_key="BOB")
queue = Queue(name=queue_name, exchange=exchange, routing_key="BOB")
queue.maybe_bind(conn)
queue.declare()
counter = 0
def publish_example(producer):
    producer.publish("Hello there: " + str(counter))
def publish_iris_data(producer):
    with open(iris_path) as f:
        lines = f.readlines()
        r = random.randrange(0, len(lines) ) 
        line = lines[r]
        data = line.split(',')
        body = '{ "signature_name":"predict", "instances": [{"sepal_length":[' + data[0] + '], "sepal_width":[' + data[1] + '], "petal_length":[' + data[2] + '], "petal_width":[' + data[3] + '] }]}'

    producer.publish(body)
def publish_mnist_data(producer):
    list_of_files = os.listdir(mnist_data_path)
    r = random.randrange(0, len(list_of_files) )
    file_to_read = list_of_files[r]

    img = Image.open(mnist_data_path + '/' +    file_to_read)
    arr = np.array(img)
    shape = arr.shape

    flat_arr = arr.ravel()

    flat_arr = flat_arr.astype(np.float32)
    flat_arr = np.multiply(flat_arr,1.0/255.0)
    flat_arr = flat_arr.tolist()
    data={"signature_name":"predict_images","instances":[{"images":flat_arr}]}
    data1 = json.dumps(data)
    producer.publish(data1)
def produce(producer):
    if type_of_model == 'iris':
        publish_iris_data(producer)
    elif type_of_model == 'mnist':
        publish_mnist_data(producer)
    else:
        publish_example(producer)
        
while True:
    produce(producer)
    #producer.publish("Hello there: " + str(counter))
    print 'Message sent: ', counter
    counter += 1
    time.sleep(30)