
class Sensor(object):
    #Constructor
    def __init__(self, name,sensor_type='ONE_WAY'):
        self.sensor_type = sensor_type
        self.name = name
    def getName(self):
    	return self.name
    def getType(self):
        return self.sensor_type

    def generateData(self):
        return None
    def executeCommand(self):
    	pass