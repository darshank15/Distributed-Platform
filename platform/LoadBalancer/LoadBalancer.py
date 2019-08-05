from flask import Flask
from flask import session
from flask import redirect, url_for
from flask import render_template
from flask import request
from flask import jsonify
from flask import abort
import json
import random
import time
server_config = 'servers.json'
service_config = 'services.config'
import sys
from Logger import Logger
import logging
import os

my_logger = logging.getLogger('test_logger')
my_logger.setLevel(logging.DEBUG)
argument_list = sys.argv
rmq_host = argument_list[1]
# rabbitmq handler
ip = argument_list[2]
#port = argument_list[3]
port = 5003
host_url = ip + ":" + str(port)
logHandler = Logger(uri='amqp://admin:admin@' + rmq_host + '//', host_url=host_url)

# adding rabbitmq handler
my_logger.addHandler(logHandler)


#python LoadBalancer.py '

class Service:
    def __init__(self, serviceName):
        self.serviceName = serviceName
        self.serviceInstances = []
        

    def addInstance(self, IP, PORT):
        url = IP + ":" + str(PORT)
        if url in self.serviceInstances:
            return False
        self.serviceInstances.append(url)
        return True
    def removeInstance(self, IP, PORT):
        url = IP + ":" + str(PORT)
        self.serviceInstances.remove(url)
    def getServiceName(self):
        return self.serviceName
    def getRunningInstances(self):
        return self.serviceInstances
    
    

    
class Server:
    ID = 0
    def __init__(self, serverIP, username, password, isExclusive, location):
        self.serverID = Server.ID + 1
        self.serverIP = serverIP
        self.username = username
        self.password = password
        self.RAM = 0
        self.CPU = 10
        self.isUp = True
        self.isExclusive = isExclusive
        self.location = location
        self.services = []
        Server.ID += 1
    def getLocation(self):
        return self.location
    def updateStatus(self, val):
        self.isUp = val
    def getExclusive(self):
        return self.isExclusive
    def getAllServices(self):
        return self.services
    def addService(self, serviceName):
        self.services.append(serviceName)
    def removeService(self, serviceName):
        print 'Before removing:', self.services
        self.services.remove(serviceName)
        for service in self.services:
            if service == serviceName:
                print service
                print type(service)
        print self.services
        print 'Removing :', serviceName
    def updateUtilization(self, RAM, CPU):
        self.RAM = RAM
        self.CPU = CPU
    def getRAM(self):
        return self.RAM
    def getCPU(self):
        return self.CPU
    def getUsername(self):
        return self.username
    def getStatus(self):
        return self.isUp
    def getPassword(self):
        return self.password
    def getServerIP(self):
        return self.serverIP
    

class LoadBalancer:
    def __init__(self, server_config, service_config):
        self.servers = {}
        self.services = {}
        for serverIP in self.read_server_config(server_config):
            ip, username, password, exclusive, location = serverIP.split(":")
            print ip
            self.servers[ip ] = Server(ip, username, password, exclusive, location)
            
        #self.read_service_config(service_config)
    def getAllServers(self):
        result = []

        for key in self.servers.keys():
            print key
            s = self.servers[key]
            data = {}
            if s.getStatus() == True:
                data['ip'] = key
                data['status'] = s.getStatus()
                data['cpu'] = s.getCPU()
                data['ram'] = s.getRAM()
                data['exclusive'] = s.getExclusive()
                data['location'] = s.getLocation()
                result.append(data)
        return result
    def getExclusiveServer(self):
        temp_server = ''
        for key in self.servers:
            server = self.servers[key]
            print 'Services:', key, server.getAllServices()
            if server.getLocation() != 'Gateway' and  server.getExclusive() == 'True' and len(server.getAllServices() ) == 0:
                temp_server = key 
                break
        result = {}
        #temp_server = '192.168.43.149'
        if temp_server == '':
            result['status'] = 'No Exclusive servers available'
            return result
        my_server = self.servers[temp_server]
        result['ip'] = temp_server
        result['username'] = my_server.getUsername()
        result['password'] = my_server.getPassword()

        return result
    def getFreeServer(self):
        load = 101
        temp_server = ''
        my_server = ''
        for server_name in self.servers:
            server = self.servers[server_name]
            if server.getLocation() == 'Gateway' or server.getExclusive() == 'True' or server.getStatus() == False or server.getUsername() not in ['dhawal','vatsal', 'priyendu',  'rushit']:
                continue
            if server.getCPU() < load:
                temp_server = server.getServerIP()
                my_server = server
                load = server.getCPU()
        result = {}
        #temp_server = '192.168.43.149'
        my_server = self.servers[temp_server]
        result['ip'] = temp_server
        result['username'] = my_server.getUsername()
        result['password'] = my_server.getPassword()

        return result
    def getLeastLoadInstance(self, instances):
        load = 101
        temp_server = ''
        for instance in instances:
            ip,port = instance.split(':')
            server = self.servers[ip]
            if server.getCPU() < load:
                temp_server = instance
        return temp_server
    def getAllServices(self):
        result = {}
        result['services'] = []
        result['servers'] = []
        for service in self.services:
            services_data = {}
            services_data['serviceName'] = self.services[service].getServiceName()
            services_data['instances'] = self.services[service].getRunningInstances()
            result['services'].append(services_data)
        result['servers'] = self.getAllServers()
        return result    

    def getServiceInstance(self, serviceName):
        if serviceName not in self.services:
            return "Service not registered"
        instances = self.services[serviceName].getRunningInstances()
        print instances
        instance = self.getLeastLoadInstance(instances)
        print 'Instance:', instance.split(':')
        ip, port = instance.split(':')
        server = self.servers[ip]
        result = {  }
        result['username'] = server.getUsername()
        result['password'] = server.getPassword()
        result['ip'] = ip
        result['port'] = port
        return result
    def getServerStats(self, ip):
        result = {}
        result['CPU'] = self.servers[ip].getCPU()
        result['RAM'] = self.servers[ip].getRAM()
        return result
    def registerService(self, serviceName, IP, PORT):
        if serviceName in self.services:
            service = self.services[serviceName]
            status = service.addInstance(IP,PORT)
        else:
            service = Service(serviceName)
            status = service.addInstance(IP,PORT)
            self.services[serviceName] = service
        if status == True:
            self.servers[IP].addService(serviceName)
    def findServerLocation(self, ip):
        return self.servers[ip].getLocation()
    def updateServerStatus(self, IP, status):
        if status == 'True':
            status = True
        else:
            status = False
        self.servers[IP].updateStatus(status)
    def unregisterService(self, serviceName, IP, PORT):
        server = self.servers[IP]
        self.services[serviceName].removeInstance(IP, PORT )
        if len(self.services[serviceName].getRunningInstances() ) == 0:
            del self.services[serviceName]
        self.servers[IP].removeService(serviceName)

    def updateUtilization(self, serverIP, RAM, CPU):
        self.servers[serverIP].updateUtilization(RAM, CPU) 
    def read_service_config(self, service_config):
        with open(service_config) as f:
            d = json.load(f )
            service = Service(d['serviceName'])
            for instance in d['instances']:
                ip, port = instance['serverIP'].split(":")
                service.addServer( self.servers[ ip ], port)
            self.services[d['serviceName'] ] = service
        

    def read_server_config(self, server_config):
        server_data = []
        with open(server_config) as f:
            d = json.load(f )
            
            for instance in d['servers']:
                ip = instance['serverIP']
                username = instance['username']
                password = instance['password']
                isExclusive = instance['isExclusive']
                location = instance['location']
                val = ip + ":" + username + ":" + password + ":" + isExclusive + ":" + location
                print val
                server_data.append(val)
               

        return server_data

load_balancer = LoadBalancer(server_config, service_config)

app = Flask(__name__)
@app.route('/')
def index():
    return 'Load balancer'
@app.route('/find_server_location/<ip>')
def find_server_location(ip):
    return jsonify(load_balancer.findServerLocation(ip) )

@app.route('/get_all_servers')
def get_all_servers():
    return jsonify(load_balancer.getAllServers())
@app.route('/get_exclusive_server')
def get_exclusive_server():
    return json.dumps(load_balancer.getExclusiveServer() )
@app.route('/get_free_server')
def get_free_server():
    return json.dumps(load_balancer.getFreeServer() ) 
@app.route('/get_all_services')
def get_all_services():
    return jsonify(load_balancer.getAllServices())
@app.route('/get_service_ip/<service_name>')
def get_service_ip(service_name):
    my_logger.debug('LoadBalancer \t get_service_ip ' + service_name)

    return jsonify( load_balancer.getServiceInstance(service_name) )
@app.route('/get_server_stats/<ip>')
def get_server_stats(ip):
    return jsonify( load_balancer.getServerStats(ip) )
@app.route('/register_service', methods=['POST'])
def register_service():
    if request.method =='POST':
        print 'Inside post'
        data = request.json
        print data
        ip = data['IP']
        port = data['PORT']
        serviceName = data['serviceName']
        time.sleep(1)
        load_balancer.registerService( serviceName , ip , port)
    return jsonify('{"Message":"Registered successfully"')
@app.route('/get_unregister_service/<service_data>')
def get_unregister_service(service_data):
    serviceName, ip, port = service_data.split(";")
    load_balancer.unregisterService( serviceName , ip , port)
    return jsonify('{"Message":"UnRegistered successfully"')
@app.route('/unregister_service', methods=['POST'])
def unregister_service():
    if request.method =='POST':
        print 'Inside post'
        data = request.json
        print data
        print type(data)
        ip = data['IP']
        port = data['PORT']
        serviceName = data['serviceName']
        load_balancer.unregisterService( serviceName , ip , port)
    return jsonify('{"Message":"UnRegistered successfully"')
@app.route('/update_server_status', methods=['POST'])
def update_server_status():
    if request.method =='POST':
        print 'Inside post'
        data = request.json
        print data
        ip = data['IP']
        val = data['status']
        load_balancer.updateServerStatus( ip, val)
    return jsonify('{"Message":"UnRegistered successfully"')

@app.route('/update_server_utilization', methods=['POST'])
def update_server_utilization():
    my_logger.debug('LoadBalancer \t update_server_utilization ' + str(request.json) )

    print 'Inside update'
    if request.method =='POST':
        print 'Inside post'
        data = request.json
        ip = data['LocalIP']
        print ip
        ram = data['RAM_USAGE']
        print ram
        cpu = data['CPU']
        load_balancer.updateUtilization(ip, ram, cpu)
    return jsonify('{"Message":"Updated successfully"')
if __name__ == '__main__':
    print 'STARTED LOAD BALANCER'
    app.run(debug=False, host='0.0.0.0',port=port)