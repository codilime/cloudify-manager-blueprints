#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

NGINX_SERVICE_NAME = 'nginx'

ctx.logger.info('Starting Nginx Service...')
utils.start_service(NGINX_SERVICE_NAME, append_prefix=False)
utils.systemd.verify_alive(NGINX_SERVICE_NAME, append_prefix=False)

nginx_url = 'http://127.0.0.1'
utils.verify_service_http(NGINX_SERVICE_NAME, nginx_url)
