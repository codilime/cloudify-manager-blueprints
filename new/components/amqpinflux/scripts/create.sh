#!/bin/bash -e

. $(ctx download-resource "components/utils")

export AMQPINFLUX_RPM_SOURCE_URL=$(ctx node properties amqpinflux_rpm_source_url)
export AMQPINFLUX_SOURCE_URL=$(ctx node properties amqpinflux_module_source_url)  # (e.g. "https://github.com/cloudify-cosmo/cloudify-amqp-influxdb/archive/3.2.zip")

export AMQPINFLUX_HOME="/opt/amqpinflux"
export AMQPINFLUX_VIRTUALENV_DIR="${AMQPINFLUX_HOME}/env"

ctx logger info "Installing AQMPInflux..."

copy_notice "amqpinflux"
create_dir "${AMQPINFLUX_HOME}"

yum_install ${AMQPINFLUX_RPM_SOURCE_URL}
create_virtualenv "${AMQPINFLUX_VIRTUALENV_DIR}"

[ -z "${AMQPINFLUX_SOURCE_URL}" ] || install_module ${AMQPINFLUX_SOURCE_URL} "${AMQPINFLUX_VIRTUALENV_DIR}"
configure_systemd_service "amqpinflux"