#!/usr/bin/env python

import json
from os.path import join, dirname
import time
import urllib2

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA
ES_SERVICE_NAME = 'elasticsearch'
RETRIES = 10

ctx_properties = utils.ctx_factory.get(ES_SERVICE_NAME)
ES_ENDPOINT_IP = ctx_properties['es_endpoint_ip']
ES_ENDPOINT_PORT = ctx_properties['es_endpoint_port']


def is_elasticsearch_responding(url):
    """Check if url responds with a correct elasticsearch status."""
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError:
        return False

    data = response.read()
    try:
        parsed_response = json.loads(data)
    except ValueError:
        return False

    if parsed_response['status'] != 200:
        return False

    return True


if not ES_ENDPOINT_IP:
    ctx.logger.info('Starting Elasticsearch Service...')
    utils.start_service(ES_SERVICE_NAME, append_prefix=False)

    ES_ENDPOINT_IP = '127.0.0.1'
    if utils.systemd.is_alive(ES_SERVICE_NAME):
        ctx.logger.info('Elasticsearch service is running')
    else:
        ctx.logger.error('Elasticsearch service is not running')

elasticsearch_url = 'http://{}:{}/'.format(ES_ENDPOINT_IP,
                                           ES_ENDPOINT_PORT)
for retry in range(RETRIES):
    # ES takes a while to start
    if is_elasticsearch_responding(elasticsearch_url):
        ctx.logger.info('ES responding')
        break
    else:
        ctx.logger.info('ES not responding (retrying {}... {})'.format(
            elasticsearch_url, retry + 1))
        time.sleep(3)
else:
    ctx.logger.error('ES didnt respond in {} tries'.format(RETRIES))
