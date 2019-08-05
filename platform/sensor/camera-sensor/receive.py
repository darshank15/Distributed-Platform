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
    # print(" [x] Received %r" % body)
    print(" [x] Received Picture")

    json_load = json.loads(body)
    a_restored = np.asarray(json_load["img"])
    #print(a_restored)
    print(a_restored.shape)

    my_int = random.randint(0, 10000)
    index = str(my_int)
    #pygame.image.save(body,"received_"+index+".jpg")
    imwrite("received_"+index+".jpg",a_restored)

    #time.sleep(2)
    print (" [x] Done")
    channel.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(queue='hello',
                      auto_ack=False,
                      on_message_callback=callback)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()