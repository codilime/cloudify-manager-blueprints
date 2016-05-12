#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

INFLUX_SERVICE_NAME = 'influxdb'

utils.upgrade_validation_directories(INFLUX_SERVICE_NAME)

if not utils.systemd.is_alive(INFLUX_SERVICE_NAME):
    raise RuntimeError('InfluxDB service must be running to allow data '
                       'migration')
