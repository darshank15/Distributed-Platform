#!/usr/bin/env python
import pika
import random, os, time, json, sys
import numpy as np
import pandas as pd
from Sensor import Sensor

class SonarSensor(Sensor):
	def __init__(self):
		super().__init__('SONAR')
	def generateData(self):
	    '''
	    Sonar Data([60*1] vector)
	    Rate : Every 10 seconds
	    '''
	    df = pd.read_csv("./sonar.all-data")
	    X = df[df.columns[0:60]].values
	    distrinution = random.randint(0, X.shape[0]-1)
	    return X[distrinution]
