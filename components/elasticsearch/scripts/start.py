#!/usr/bin/env python

import json
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA
ES_SERVICE_NAME = 'elasticsearch'

ctx_properties = utils.ctx_factory.get(ES_SERVICE_NAME)
ES_ENDPOINT_IP = ctx_properties['es_endpoint_ip']
ES_ENDPOINT_PORT = ctx_properties['es_endpoint_port']


def check_elasticsearch_response(response):
    """Check if the response from elasticsearch is correct.

    A correct response has a status of 200, and also returns a JSON object
    with {'status': 200}.
    """
    if response.code != 200:
        return False

    data = response.read()
    parsed_response = json.loads(data)

    return parsed_response['status'] == 200


if not ES_ENDPOINT_IP:
    ctx.logger.info('Starting Elasticsearch Service...')
    utils.start_service(ES_SERVICE_NAME, append_prefix=False)
    ES_ENDPOINT_IP = '127.0.0.1'
    utils.systemd.verify_alive(ES_SERVICE_NAME, append_prefix=False)

elasticsearch_url = 'http://{}:{}/'.format(ES_ENDPOINT_IP,
                                           ES_ENDPOINT_PORT)

utils.verify_service_http(ES_SERVICE_NAME, elasticsearch_url,
                          check_elasticsearch_response)
