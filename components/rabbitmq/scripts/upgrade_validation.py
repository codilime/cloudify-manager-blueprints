#!/usr/bin/env python

from os.path import join, dirname
from cloudify import ctx
ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA

RABBITMQ_SERVICE_NAME = 'rabbitmq'

install_properties = utils.ctx_factory.get_install_properties(
    RABBITMQ_SERVICE_NAME)
upgrade_properties = utils.ctx_factory._load_ctx_properties(
    RABBITMQ_SERVICE_NAME)

IMMUTABLE_PROPERTIES = [
    'rabbitmq_username',
    'rabbitmq_pasword',
    'rabbitmq_endpoint_ip',
    'rabbitmq_ssl_enabled',
    'broker_cert_path'
]


def verify_properties(install_properties, upgrade_properties):
    """Compare node properties and decide if upgrading is allowed.

    When upgrading the manager, some RabbitMQ inputs must remain the same
    because the running node instances might be using them.
    """
    changed = []
    for property_name in IMMUTABLE_PROPERTIES:
        original_property = install_properties.get(property_name)
        upgrade_property = upgrade_properties.get(property_name)

        if original_property != upgrade_property:
            changed.append(property_name)

    if changed:
        ctx.abort_operation(
            'RabbitMQ properties must not change during a manager '
            'upgrade! Changed properties: {0}'.format(', '.join(changed)))


utils.upgrade_validation_directories(RABBITMQ_SERVICE_NAME)
verify_properties(install_properties, upgrade_properties)
