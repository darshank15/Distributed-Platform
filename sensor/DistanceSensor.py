#!/usr/bin/env python
import pika
import random, os, time, json, sys
import numpy as np
import pandas as pd
from Sensor import Sensor

class DistanceSensor(Sensor):


    def __init__(self):
        super().__init__("DISTANCE", "TWO_WAY")
        self.data = []
    def to_output_file(self, distance):
        f = open("distance.txt", "w")
        f.write("Distance : "+str(distance))
        f.close()


    def getType(self):
        return super().getType()


    def generateData(self):
        '''
        90% of the values are between (201, 1000) and 10% of the values are between (0,200)
        Rate : one value every second
        '''
        distribution = random.randint(1,10)
        distance = 0
        if(distribution == 1):
            distance = random.randint(0, 200)
        else:
            distance = random.randint(201, 1000)
        self.to_output_file(distance)
        self.data.append(distance)
        return distance


    def executeCommand(self, command):
        if command == 'max':
            return max(self.data)
            #return 'COMMAND: ' + command

        #outputDistance me write  //thread