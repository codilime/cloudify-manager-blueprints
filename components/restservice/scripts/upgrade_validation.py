#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

REST_SERVICE_NAME = 'restservice'

utils.upgrade_validation_directories(REST_SERVICE_NAME)

install_properties = utils.ctx_factory.get(REST_SERVICE_NAME,
                                           upgrade_props=False)

upgrade_properties = utils.ctx_factory.get(REST_SERVICE_NAME)
ctx.logger.info('elo {}'.format(upgrade_properties))