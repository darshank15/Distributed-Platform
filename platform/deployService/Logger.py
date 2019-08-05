from kombu import Connection, Exchange, Queue, Producer
import logging
import datetime
import psutil
import os
import psutil
import socket
class Logger(logging.Handler):
    """
     A handler that acts as a RabbitMQ publisher
     Requires the kombu module.

     Example setup::

        handler = RabbitMQHandler('amqp://guest:guest@localhost//', queue='my_log')
    """
    def __init__(self, uri=None, queue='logging'):
        logging.Handler.__init__(self)
        if uri:
            connection = Connection(uri)

        self.queue = connection.SimpleQueue(queue)

    def emit(self, record):

        pid = os.getpid()
        process = psutil.Process(pid)
        process_name = process.name()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        local_ip_address = s.getsockname()[0]
        message = record.msg.split('\t')
        service_name = message[0]
        message = ''.join(message[1:])
        result = {
            "pid" : pid,
            "process_name": process_name,
            "timestamp": str(datetime.datetime.now()),
            "service_name": service_name,
            "message": message,
            "ip": local_ip_address
        }
        self.queue.put(str(result) )

    def close(self):
        self.queue.close()