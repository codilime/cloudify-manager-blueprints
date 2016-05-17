#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

LOGSTASH_SERVICE_NAME = 'logstash'

utils.upgrade_validation_directories(LOGSTASH_SERVICE_NAME)
utils.systemd.verify_alive(LOGSTASH_SERVICE_NAME, append_prefix=False)
