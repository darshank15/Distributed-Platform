#!/usr/bin/env python
import pika
import time
import pygame
import random as random
import json
from cv2 import *
import numpy as np

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello', durable=True)

def callback(ch, method, properties, body):
    print("Received Data"+str(body))

    json_load = json.loads(body)
    print ("Data : "+str(json_load['data']))
    channel.basic_ack(delivery_tag = method.delivery_tag)

data = channel.basic_consume(queue='hello',
                      auto_ack=False,
                      on_message_callback=callback)
print(' [*] Waiting for messages. To exit press CTRL+C'+(data))
#channel.start_consuming()
#amqp://guest:guest@localhost:5672/%2F