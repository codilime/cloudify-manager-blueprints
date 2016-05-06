#!/usr/bin/env python

import socket
from cloudify import ctx

from utils import systemd


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = ctx.instance.runtime_properties['broker_port']

try:
    sock.connect(('127.0.0.1', PORT))
except socket.error as e:
    ctx.logger.critical(
        'RabbitMQ was not listening on port {}: {}'.format(PORT, e))
else:
    ctx.logger.info('RabbitMQ was listening on port {}'.format(PORT))
    sock.shutdown(socket.SHUT_RDWR)
finally:
    sock.close()


ctx.logger.error(
    'ta {}'.format(systemd.systemctl('status', 'cloudify-rabbitmq'))
