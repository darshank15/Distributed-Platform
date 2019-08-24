from kombu import Connection, Exchange, Queue, Consumer
import socket
import sys
import json
import requests
config_data = {}
argument_list = sys.argv

url = argument_list[1]
lb = argument_list[2]
server_url = lb + '/update_server_utilization'
def process_message(body, message):
    #print("The body is {}".format(body))
    print 'Inside process'
    message.ack()   
    print 'Message:', body
    #service_name = body['serviceName']
    ram = body['RAM_USAGE']
    cpu = body['CPU']
    ip = body['LocalIP']
    print ram, cpu
    #data = json.loads('{"RAM_USAGE":"10", "CPU":"5", "LocalIP":"10.42.0.41"}')
    print 'Data:', body
    headers = {'Content-type':'application/json'}
    try:
        print requests.post(server_url, json=body , headers=headers)
    except Exception as e:
        print 'Exception'
        print e
    '''
    if float(config_data[service_name]['maxRAM']) < float(ram) or float(config_data[service_name]['maxCPU']) < float(cpu):
        print 'Start Instance of Service:', service_name
    elif float(config_data[service_name]['minRAM']) > float(ram) or float(config_data[service_name]['minCPU']) > float(cpu):
        print 'Kill Instance of Service:', service_name
    '''



def establish_connection():
    revived_connection = conn.clone()
    revived_connection.ensure_connection(max_retries=3)
    channel = revived_connection.channel()
    
    consumer.revive(channel)
    consumer.consume()
    return revived_connection
def consume():
    new_conn = establish_connection()
    print 'Connectin establised'
    while True:
        try:
            new_conn.drain_events()
        except socket.timeout:
            new_conn.heartbeat_check()
            print 'Exception: time out'

def run():
    while True:
        try:
            consume()
        except conn.connection_errors:
            print("connection revived")

def read_monitor_config(threshold_config):
    config_data = {}
    with open(threshold_config) as f:
        for line in f.readlines():
            d = json.loads(line)
            config_data[d['serviceName']] = {}
            config_data[d['serviceName']]['maxRAM'] = d['maxRAM']
            config_data[d['serviceName']]['minRAM'] = d['minRAM']
            config_data[d['serviceName']]['minCPU'] = d['minCPU']
            config_data[d['serviceName']]['maxCPU'] = d['maxCPU']
    return config_data


exchange_name = 'exchange-server-stats'
queue_name = 'server-stats-queue'
threshold_config = 'monitor_server_threshold.config'
topology_config = 'topology.config'
#config_file_name = argument_list[4]
rabbit_url = "amqp://admin:admin@" + url + ":5672/"
config_data = read_monitor_config(threshold_config)
print 'Config data:', config_data
conn = Connection(rabbit_url)
channel = conn.channel()
exchange = Exchange(exchange_name, type="direct")
queue = Queue(name=queue_name, exchange=exchange, routing_key="Stats123")
consumer = Consumer(conn, queues=queue, callbacks=[process_message], accept=["application/json"])
#consumer.consume()
run()