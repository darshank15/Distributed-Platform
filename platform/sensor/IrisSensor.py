#!/usr/bin/env python
import pika
import random, os, time, json, sys
import numpy as np
import pandas as pd
from Sensor import *

class IrisSensor(Sensor):
	def __init__(self):
		super().__init__('CAMERA')
	def generateData(self):
	    '''
	    Iris Data([4*1] vector)
	    Rate : Every 0.5 second
	    '''
		url='http://192.168.43.32:8080/shot.jpg'
		imgResp=urllib.urlopen(url)
		imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
		img=cv2.imdecode(imgNp,-1)
		print("streaming a pic from sensor..")
		#time.sleep(15)
		return img