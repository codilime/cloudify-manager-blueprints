#!/usr/bin/env python

from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

LOGSTASH_SERVICE_NAME = 'logstash'


ctx.logger.info('Starting Logstash Service...')
utils.start_service(LOGSTASH_SERVICE_NAME, append_prefix=False)

if utils.systemd.is_alive(LOGSTASH_SERVICE_NAME, append_prefix=False):
    ctx.logger.info('Logstash service is running')
else:
    ctx.logger.error('Logstash service is not running')
