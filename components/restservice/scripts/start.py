#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

REST_SERVICE_NAME = 'restservice'


ctx.logger.info('Starting Cloudify REST Service...')
utils.start_service(REST_SERVICE_NAME)

utils.systemd.verify_alive(REST_SERVICE_NAME)

restservice_url = 'http://{}:{}'.format('127.0.0.1', 8100)
utils.verify_service_http(REST_SERVICE_NAME, restservice_url)
