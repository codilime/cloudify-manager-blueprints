#!/usr/bin/env python

from os.path import join, dirname
import time

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA

MGMT_WORKER_SERVICE_NAME = 'mgmtworker'
CELERY_PATH = '/opt/mgmtworker/env/bin/celery'  # also hardcoded in create
RETRIES = 10

ctx_properties = utils.ctx_factory.get_install_properties(
    MGMT_WORKER_SERVICE_NAME)


def is_worker_running(amqp_url):
    """Use `celery status` to check if the worker is running."""
    resp = utils.sudo([
        CELERY_PATH,
        '-b', celery_amqp_url,
        '--app=cloudify_agent.app.app',
        'status'
    ], ignore_failures=True)
    return resp.returncode == 0


ctx.logger.info('Starting Management Worker Service...')
utils.start_service_and_archive_properties(MGMT_WORKER_SERVICE_NAME)

if utils.systemd.is_alive(MGMT_WORKER_SERVICE_NAME):
    ctx.logger.info('Management Worker Service is running')
else:
    ctx.logger.error('Management Worker Service is not running')

celery_amqp_url = ('amqp://{rabbitmq_username}:{rabbitmq_password}@'
                   '{rabbitmq_endpoint_ip}:{port}//').format(
    port=5672, **ctx_properties)

for retry in range(RETRIES):
    if is_worker_running(celery_amqp_url):
        ctx.logger.info('Celery worker is running')
        break
    else:
        time.sleep(1)
        ctx.logger.info('Celery worker not running (retrying... {}'.format(
            retry))
else:
    ctx.logger.error('Celery worker was not running after {} retries'.format(
        RETRIES))
