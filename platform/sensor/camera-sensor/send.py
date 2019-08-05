#!/usr/bin/env python
import pika
from image_pygame import *
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello', durable=True)
# channel.basic_publish(exchange='',
#                       routing_key='hello',
#                       body='Hello World!')

cam = MyCamera()
img = cam.pic_cv2()
#print (type(img))
input = {"img":img}
print(img.shape)
jsoninput = json.dumps(input, cls=NumpyEncoder)
channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=jsoninput)

print(" [x] Sent 'Picture!'")
connection.close()