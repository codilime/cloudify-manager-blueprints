#!/usr/bin/env python

import subprocess
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

MGMT_WORKER_SERVICE_NAME = 'mgmtworker'
CELERY_PATH = '/opt/mgmtworker/env/bin/celery'  # also hardcoded in create

ctx_properties = utils.ctx_factory.get_install_properties(
    MGMT_WORKER_SERVICE_NAME)


@utils.retry(subprocess.CalledProcessError)
def check_worker_running(amqp_url):
    """Use `celery status` to check if the worker is running."""
    return utils.sudo([
        CELERY_PATH,
        '-b', celery_amqp_url,
        '--app=cloudify_agent.app.app',
        'status'
    ])


ctx.logger.info('Starting Management Worker Service...')
utils.start_service(MGMT_WORKER_SERVICE_NAME)

utils.systemd.verify_alive(MGMT_WORKER_SERVICE_NAME)

celery_amqp_url = ('amqp://{rabbitmq_username}:{rabbitmq_password}@'
                   '{rabbitmq_endpoint_ip}:{port}//').format(
    port=5672, **ctx_properties)

check_worker_running(celery_amqp_url)
