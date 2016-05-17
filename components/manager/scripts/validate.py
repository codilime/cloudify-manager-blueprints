#!/usr/bin/env python

import urllib2
import platform
import subprocess
from os.path import join, dirname

from cloudify import ctx

ctx.download_resource(
    join('components', 'utils.py'),
    join(dirname(__file__), 'utils.py'))

import utils  # NOQA


def _error(message):
    return 'Validation Error: {0}'.format(message)


def _get_host_total_memory():
    """
    MemTotal:        7854400 kB
    MemFree:         1811840 kB
    MemAvailable:    3250176 kB
    Buffers:          171164 kB
    Cached:          1558216 kB
    SwapCached:       119180 kB
    """
    with open('/proc/meminfo') as memfile:
        memory = memfile.read()
    for attribute in memory.splitlines():
        if attribute.lower().startswith('memtotal'):
            return int(attribute.split(':')[1].strip().split(' ')[0]) / 1024


def _get_available_host_disk_space():
    """
    Filesystem                 Type 1G-blocks  Used Available Use% Mounted on
    /dev/mapper/my_file_system ext4      213G   63G      139G  32% /
    """
    df = subprocess.Popen(["df", "-BG", "/etc/issue"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    available_disk_space_in_gb = output.split("\n")[1].split()[3].rstrip('G')
    return int(available_disk_space_in_gb)


def _get_os_distro():
    distro, version, _ = \
        platform.linux_distribution(full_distribution_name=False)
    return distro.lower(), version.split('.')[0]


def _validate_sufficient_memory(min_memory_required_in_mb):
    current_memory = _get_host_total_memory()
    ctx.logger.info('Validating memory requirement...')
    if int(min_memory_required_in_mb) >= int(current_memory):
        return _error(
            'The provided host does not have enough memory to run '
            'Cloudify Manager (Current: {0}MB, Required: {1}MB).'.format(
                current_memory, min_memory_required_in_mb))


def _validate_sufficient_disk_space(min_disk_space_required_in_gb):
    available_disk_space_in_gb = _get_available_host_disk_space()

    ctx.logger.info('Validating disk space requirement...')
    if int(available_disk_space_in_gb) < int(min_disk_space_required_in_gb):
        return _error(
            'The provided host does not have enough disk space to run '
            'Cloudify Manager (Current: {0}GB, Required: {1}GB).'.format(
                available_disk_space_in_gb, min_disk_space_required_in_gb))


def _validate_es_heap_size(es_heap_size, allowed_gap_in_mb):
    """
    If the heapsize exceeds the hosts memory minus an allowed gap, fail.
    The allowed gap is the memory we require to be available for all other
    services.
    """
    try:
        es_heap_size_in_mb = utils.parse_jvm_heap_size(es_heap_size)
    except ValueError:
        return _error(
            'elasticsearch_heap_size input is invalid. '
            'The input size can be one of `Xm` or `Xg` formats. '
            'Provided: {0}'.format(es_heap_size))

    current_memory = _get_host_total_memory()
    available_memory_for_heap = \
        abs(int(current_memory) - int(allowed_gap_in_mb))
    ctx.logger.info('Validating Elasticsearch heap size requirement...')
    if int(es_heap_size_in_mb) > available_memory_for_heap:
        additional_required_memory = \
            abs(available_memory_for_heap - int(es_heap_size_in_mb))
        return _error(
            'The heapsize provided for Elasticsearch ({0}MB) exceeds the '
            'host\'s memory minus the allowed gap of {1}MB. '
            'Cloudify Manager (Current: {2}MB, Additional required memory: '
            '{3}MB).'.format(
                es_heap_size_in_mb,
                allowed_gap_in_mb,
                current_memory,
                additional_required_memory))


def _validate_supported_distros(supported_distros, supported_versions):
    distro, version = _get_os_distro()

    ctx.logger.info('Validating supported distributions...')
    if distro not in supported_distros or version not in supported_versions:
        one_of_string = ' or '.join(
            ['{0} {1}.x'.format(dist, ver) for dist in
             supported_distros for ver in supported_versions])
        return _error(
            'Cloudify Manager requires either {0} '
            'to run (Provided: {1} {2})'.format(
                one_of_string, distro, version))


def _validate_resources_package_url(manager_resources_package_url):
    try:
        urllib2.urlopen(manager_resources_package_url)
    except urllib2.HTTPError as ex:
        return _error(
            "The Manager's Resources Package {0} is "
            "not accessible (HTTP Error: {1})".format(
                manager_resources_package_url, ex.code))
    except urllib2.URLError as ex:
        return _error(
            "The Manager's Resources Package {0} is "
            "invalid (URL Error: {1})".format(
                manager_resources_package_url, ex.args))


def validate():
    ignore_validations = ctx.node.properties['ignore_bootstrap_validations']
    # remove last character as it contains the `g` or `m`.
    es_heap_size = ctx.node.properties['es_heap_size']
    resources_package_url = ctx.node.properties['manager_resources_package']

    error_summary = []

    error_summary.append(_validate_supported_distros(
        supported_distros=('centos', 'redhat'),
        supported_versions=('7')))
    error_summary.append(_validate_sufficient_memory(
        min_memory_required_in_mb=4096))
    error_summary.append(_validate_sufficient_disk_space(
        min_disk_space_required_in_gb=5))
    error_summary.append(_validate_es_heap_size(
        es_heap_size=es_heap_size, allowed_gap_in_mb=1024))
    if resources_package_url:
        error_summary.append(_validate_resources_package_url(
            resources_package_url))

    # if no error occured in a validation, we need to remove its reference.
    error_summary = [error for error in error_summary if error]
    if error_summary:
        printable_error_summary = '\n' + '\n'.join(error_summary)
        if ignore_validations:
            ctx.logger.warn('Ignoring validation errors. {0}'.format(
                printable_error_summary))
        else:
            ctx.abort_operation(printable_error_summary)


if __name__ == '__main__':
    validate()
