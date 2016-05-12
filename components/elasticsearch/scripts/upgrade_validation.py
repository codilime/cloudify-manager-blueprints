#!/usr/bin/env python

import json

from os.path import join, dirname
from cloudify import ctx
import urllib2

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

ES_SERVICE_NAME = 'elasticsearch'

utils.upgrade_validation_directories(ES_SERVICE_NAME)

install_properties = utils.ctx_factory.get_install_properties(
    ES_SERVICE_NAME)
upgrade_properties = utils.ctx_factory._load_ctx_properties(
    ES_SERVICE_NAME)
ES_ENDPOINT_IP = install_properties['es_endpoint_ip']
if not ES_ENDPOINT_IP:
    ES_ENDPOINT_IP = '127.0.0.1'

if not utils.systemd.is_alive(ES_SERVICE_NAME, append_prefix=False):
    raise RuntimeError('Elasticsearch must be running to allow data migration')


es_status = json.load(
    urllib2.urlopen('http://{}:9200/'.format(ES_ENDPOINT_IP)))

if es_status['status'] != 200:
    raise RuntimeError('Elasticsearch returned a malformed response')


es_jvm_stats = json.load(
    urllib2.urlopen('http://{}:9200/_nodes/stats/jvm'.format(
        ES_ENDPOINT_IP)))

total_heap_bytes_used = sum(
    node_data['jvm']['mem']['heap_used_in_bytes']
    for node_data in es_jvm_stats['nodes'].values()
)

heap_used_in_mb = total_heap_bytes_used // (1024 ** 2)
# TODO use the function from validate.py - factor out to utils
es_heap_size = upgrade_properties['es_heap_size']

if es_heap_size.endswith('g'):
    multiplier = 10**3
elif es_heap_size.endswith('m'):
    multiplier = 1
else:
    raise ValueError('elasticsearch_heap_size input is invalid. '
                     'The input size can be one of `Xm` or `Xg` formats. '
                     'Provided: {0}'.format(es_heap_size))

es_heap_size_in_mb = int(es_heap_size[:-1]) * multiplier

if heap_used_in_mb > es_heap_size_in_mb:
    raise RuntimeError('New Elasticsearch heap size ({}) is not enough for '
                       'the current ES heap ({} MiB)'.format(es_heap_size,
                                                             heap_used_in_mb))
