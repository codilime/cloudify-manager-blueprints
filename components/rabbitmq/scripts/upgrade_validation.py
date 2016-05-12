#!/usr/bin/env python

from os.path import join, dirname, exists
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

# these properties must not change in an upgrade
IMMUTABLE_PROPERTIES = [
    'rabbitmq_username',
    'rabbitmq_pasword',
    'rabbitmq_endpoint_ip',
    'rabbitmq_ssl_enabled',
    'broker_cert_path'
]

changed = []
for property_name in IMMUTABLE_PROPERTIES:
    original_property = install_properties.get(property_name)
    upgrade_property = upgrade_properties.get(property_name)

    if original_property != upgrade_property:
        changed.append(property_name)

if changed:
    raise RuntimeError(
        'RabbitMQ properties must not change during a manager '
        'upgrade! Changed properties: {}'.format(', '.join(changed)))

if exists(
        utils.ctx_factory._get_rollback_properties_dir(RABBITMQ_SERVICE_NAME)):
    raise RuntimeError('Rollback properties directory exists for service {}'
                       .format(RABBITMQ_SERVICE_NAME))

if exists(
        utils.resource_factory._get_rollback_resources_dir(
            RABBITMQ_SERVICE_NAME)):
    raise RuntimeError('Rollback resources directory exists for service {}'
                       .format(RABBITMQ_SERVICE_NAME))


if not exists(
        utils.resource_factory._get_resources_dir(
            RABBITMQ_SERVICE_NAME)):
    raise RuntimeError('Resources directory does not exist for service {}'
                       .format(RABBITMQ_SERVICE_NAME))
