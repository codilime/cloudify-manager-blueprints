#!/usr/bin/env python

from os.path import join, dirname
import time
import urllib2

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

INFLUX_SERVICE_NAME = 'influxdb'


ctx_properties = utils.ctx_factory.get(INFLUX_SERVICE_NAME)

INFLUXDB_ENDPOINT_IP = ctx_properties['influxdb_endpoint_ip']
INFLUXDB_ENDPOINT_PORT = 8086
RETRIES = 10


def is_influxdb_responding(url):
    """Check if url responds with a normal influxdb response."""
    try:
        urllib2.urlopen(url).read()
    except urllib2.HTTPError as e:
        # influxdb normally responds with a 404 on GET to /
        if e.code != 404:
            return False
        return True
    except urllib2.URLError:
        return False
    else:
        return True


if not INFLUXDB_ENDPOINT_IP:
    ctx.logger.info('Starting InfluxDB Service...')
    utils.start_service_and_archive_properties(INFLUX_SERVICE_NAME)

    INFLUXDB_ENDPOINT_IP = '127.0.0.1'

    if utils.systemd.is_alive(INFLUX_SERVICE_NAME):
        ctx.logger.info('InfluxDB service is running')
    else:
        ctx.logger.error('InfluxDB service is not running')


influxdb_url = 'http://{}:{}'.format(
    INFLUXDB_ENDPOINT_IP, INFLUXDB_ENDPOINT_PORT)
for retry in range(RETRIES):
    if is_influxdb_responding(influxdb_url):
        ctx.logger.info('InfluxDB responding')
        break
    else:
        ctx.logger.info(
            'InfluxDB not responding (retrying {}... {})'.format(
                influxdb_url, retry + 1))
        time.sleep(3)
else:
    ctx.logger.error('InfluxDB didnt respond in {} tries'.format(RETRIES))
