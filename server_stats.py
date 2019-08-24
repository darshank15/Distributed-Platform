import psutil
import os
import socket
from kombu import Connection, Exchange, Queue, Producer
import time
import sys
class ServerStat:
    @staticmethod
    def get_utilization():
        result = {}
        result['CPU'] = cpu_utilitzation = psutil.cpu_percent()
        
        stats = dict(psutil.virtual_memory()._asdict())

        result['RAM_USAGE'] = stats['used'] * 100.0 / stats['total']
        return result
def get_server_stats():
    result = ServerStat.get_utilization()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    local_ip_address = s.getsockname()[0]
    result['LocalIP'] = local_ip_address
    '''
    with open(config_file_name) as f:
        for line in f.readlines():
            key, value = line.split('=')
            result[key] = value               
    '''
    return result

argument_list = sys.argv

url = argument_list[1]
exchange_name = 'exchange-server-stats'
queue_name = 'server-stats-queue'
#config_file_name = argument_list[4]
rabbit_url = "amqp://admin:admin@" + url + ":5672/"

conn = Connection(rabbit_url)
channel = conn.channel()
exchange = Exchange(exchange_name, type="direct")
producer = Producer(exchange=exchange, channel=channel, routing_key='Stats123')
queue = Queue(name=queue_name, exchange=exchange, routing_key='Stats123')
queue.maybe_bind(conn)
while True:
    msg = get_server_stats()
    print(msg)
    producer.publish(msg)
    time.sleep(60)