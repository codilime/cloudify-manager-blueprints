#!/usr/bin/env python

import urllib2
import urlparse
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

REST_SERVICE_NAME = 'restservice'
REST_SERVICE_HOME = '/opt/manager'

# this is currently hardcoded in userstore.yaml
REST_CREDENTIALS = ('admin', 'admin')


def verify_restservice(url, credentials=None):
    """To verify that the REST service is working, GET the blueprints list.

    There's nothing special about the blueprints endpoint, it's simply one
    that also requires the storage backend to be up, so if it works, there's
    a good chance everything is configured correctly.
    """
    blueprints_url = urlparse.urljoin(url, 'api/v2/blueprints')
    req = urllib2.Request(blueprints_url)

    if credentials is not None:
        auth_header = utils.basic_auth_header(*credentials)
        req.add_header('Authorization', auth_header)

    try:
        return urllib2.urlopen(req)
    except urllib2.URLError as e:
        ctx.abort_operation('REST service returned an invalid response: {0}'
                            .format(e))
        raise


ctx.logger.info('Starting Cloudify REST Service...')
utils.start_service(REST_SERVICE_NAME)

utils.systemd.verify_alive(REST_SERVICE_NAME)

restservice_url = 'http://{}:{}'.format('127.0.0.1', 8100)
utils.verify_service_http(REST_SERVICE_NAME, restservice_url)
verify_restservice(restservice_url, credentials=REST_CREDENTIALS)
