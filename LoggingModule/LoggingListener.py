from kombu import Connection, Exchange, Queue, Consumer
import datetime
import sys
import os
import socket

config_data = {}
i = 0
def process_message(body, message):
    global i
    print("The body is {}".format(body))
    print 'Inside process'
    
    file_name = config_data['logging_path'] + str(datetime.datetime.now())[:10]  + '.log'
    body = body.replace("'", "\"")
    val = '{"index":{"_index":"custom_log", "_id":' + str(i) + '}}'
    i += 1
    body = val + "\n" + str(body.encode("ascii","replace"))
    with open(file_name, 'a+') as f:
        f.write(body + '\n')

    message.ack()

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

def read_logging_config(config_file_path):
    config_data = {}
    with open(config_file_path) as f:
        for line in f.readlines():
            key, value = line.split('=')
            config_data[key] = value.strip()
    return config_data

argument_list = sys.argv

url = argument_list[1]
exchange_name = 'logging'
queue_name = 'logging'
logging_config = 'logging.config'
#config_file_name = argument_list[4]
rabbit_url = "amqp://admin:admin@" + url + ":5672/"
config_data = read_logging_config(logging_config)
print 'Config data:', config_data
print datetime.datetime.now()
conn = Connection(rabbit_url)
channel = conn.channel()
exchange = Exchange(exchange_name, type="direct")
queue = Queue(name=queue_name, exchange=exchange, routing_key="Logging123")
consumer = Consumer(conn, queues=queue, callbacks=[process_message], accept=["application/json","text/plain"])
#consumer.consume()
run()