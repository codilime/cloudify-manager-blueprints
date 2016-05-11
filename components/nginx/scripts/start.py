#!/usr/bin/env python

from os.path import join, dirname
import time
import urllib2

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))
import utils  # NOQA
NGINX_SERVICE_NAME = 'nginx'
RETRIES = 10


def is_nginx_responding(url):
    """Check if nginx responds at the url."""
    try:
        urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        # nginx might respond with any error code
        return True
    except urllib2.URLError:
        return False
    else:
        return True


ctx.logger.info('Starting Nginx Service...')
utils.start_service_and_archive_properties(NGINX_SERVICE_NAME,
                                           append_prefix=False)


if utils.systemd.is_alive(NGINX_SERVICE_NAME, append_prefix=False):
    ctx.logger.info('Nginx service is running')
else:
    ctx.logger.error('Nginx service is not running')

nginx_url = 'http://127.0.0.1'
for retry in range(RETRIES):
    if is_nginx_responding(nginx_url):
        ctx.logger.info('Nginx responding')
        break
    else:
        ctx.logger.info(
            'Nginx not responding (retrying {}... {})'.format(
                nginx_url, retry + 1))
        time.sleep(3)
else:
    ctx.logger.error('Nginx didnt respond in {} tries'.format(RETRIES))
