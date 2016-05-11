#!/usr/bin/env python

from os.path import join, dirname
import time
import urllib2

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

REST_SERVICE_NAME = 'restservice'
RETRIES = 10


def is_restservice_responding(url):
    """Check if the REST service responds at the url."""
    try:
        urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        # the REST service might respond with a 500 on a GET to /
        return True
    except urllib2.URLError:
        return False
    else:
        return True


ctx.logger.info('Starting Cloudify REST Service...')
utils.start_service(REST_SERVICE_NAME)

if utils.systemd.is_alive(REST_SERVICE_NAME):
    ctx.logger.info('REST Service is running')
else:
    ctx.logger.error('REST Service is not running')


restservice_url = 'http://{}:{}'.format('127.0.0.1', 8100)
for retry in range(RETRIES):
    if is_restservice_responding(restservice_url):
        ctx.logger.info('REST Service responding')
        break
    else:
        ctx.logger.info(
            'REST Service not responding (retrying {}... {})'.format(
                restservice_url, retry + 1))
        time.sleep(3)
else:
    ctx.logger.error('REST Service didnt respond in {} tries'.format(RETRIES))
