import json
import requests
import sys
import os

SCHEDULE_PATH = '/schedule_path'
DEPLOY_PATH = '/deploy'
NOTIFY_PATH = '/notify'
GET_GATEWAYS = '/get_gateways'
GET_SERVICES = '/get_services'
GET_SENSORS = '/get_sensors'
GET_MODELS = '/get_models'
START_SERVICE = '/start_service'
STOP_SERVICE = '/stop_service'
INFERENCE_PATH = '/get_inference'

class Wrapper(object):
    def __init__(lb_url):
        self.lb_url = lb_url
    def schedule(self, model_name):
        response = requests.post(self.lb_url + SCHEDULE_PATH, data = {"model_name":model_name} )
        return response
    def deploy(self, model_name):
        response = requests.post(self.lb_url + DEPLOY_PATH, data = { "model_name": model_name} )
    def notify(self, message, email):
        response = requests.post(self.lb_url + NOTIFY_PATH, data = {"message":message, "email":email})
        return response
    def getGateways(self):
        response = requests.get(self.lb_url + GET_GATEWAYS)
        return response
    def getSensors(self):
        response = requests.get(self.lb_url + GET_SENSORS)
        return response
    def getModels(self):
        response = requests.get(self.lb_url + GET_MODELS)
        return response
    def getServices(self):
        response = requests.get(self.lb_url + GET_SERVICES)
        return response
    def startService(self, serviceName, type='SHARED'):
        response = requests.post(self.lb_url + START_SERVICE, {"service_name":serviceName, "type":type})
        return response
    def stopService(self, serviceName):
        response = requests.get(self.lb_url + STOP_SERVICE, {"service_name":serviceName})
        return response
    def getInference(self, model_name):
        response = requests.post(self.lb_url + INFERENCE_PATH, {"model":model_name})
        return response
    