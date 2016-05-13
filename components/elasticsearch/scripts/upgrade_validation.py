#!/usr/bin/env python

import urllib2
import urlparse
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

ES_SERVICE_NAME = 'elasticsearch'

install_properties = utils.ctx_factory.get_install_properties(
    ES_SERVICE_NAME)
upgrade_properties = utils.ctx_factory._load_ctx_properties(
    ES_SERVICE_NAME)

ES_ENDPOINT_IP = install_properties['es_endpoint_ip']
if not ES_ENDPOINT_IP:
    ES_ENDPOINT_IP = '127.0.0.1'


def verify_properties(install_properties, upgrade_properties):
    """Compare node properties and decide if upgrading is allowed."""
    bootstrap_heap_size = utils.parse_jvm_heap_size(
        install_properties['es_heap_size'])
    upgrade_heap_size = utils.parse_jvm_heap_size(
        upgrade_properties['es_heap_size'])
    if upgrade_heap_size < bootstrap_heap_size:
        ctx.abort_operation('Upgrading a Cloudify Manager with Elasticsearch '
                            'Heap Size lower than what it was initially '
                            'bootstrapped with is not allowed.')


def verify_elasticsearch_running(url):
    """Check that ES is running, and that it contains the provider context.

    This is a sanity check that the manager we're upgrading was bootstrapped
    correctly.
    """
    provider_context_url = urlparse.urljoin(url, 'cloudify_storage/'
                                                 'provider_context/context')
    try:
        urllib2.urlopen(provider_context_url)
    except urllib2.URLError as e:
        ctx.abort_operation('ES returned an error when getting the provider '
                            'context: {0}'.format(e))
        raise

elasticsearch_url = 'http://{0}:9200'.format(ES_ENDPOINT_IP)

utils.upgrade_validation_directories(ES_SERVICE_NAME)
utils.systemd.verify_alive(ES_SERVICE_NAME, append_prefix=False)
verify_properties(install_properties, upgrade_properties)
verify_elasticsearch_running(elasticsearch_url)
