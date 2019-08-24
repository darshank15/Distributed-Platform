from Logger import Logger
import logging
import os

my_logger = logging.getLogger('test_logger')
my_logger.setLevel(logging.DEBUG)

# rabbitmq handler
logHandler = Logger('amqp://admin:admin@localhost//', host_url='10.1.37.64')

# adding rabbitmq handler
my_logger.addHandler(logHandler)
my_logger.debug('LoggerTest Service \t hello')

