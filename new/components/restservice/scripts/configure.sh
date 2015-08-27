#!/bin/bash -e

. $(ctx download-resource "components/utils")

CONFIG_REL_PATH="components/restservice/config"
REST_SERVICE_HOME="/opt/manager"

ctx logger info "Configuring logrotate..."
lconf="/etc/logrotate.d/gunicorn"

cat << EOF | sudo tee $lconf > /dev/null
$REST_SERVICE_LOG_PATH/*.log {
        daily
        missingok
        rotate 7
        compress
        delaycompress
        notifempty
        sharedscripts
        postrotate
                [ -f /var/run/gunicorn.pid ] && kill -USR1 \$(cat /var/run/gunicorn.pid)
        endscript
}
EOF

sudo chmod 644 $lconf

ctx logger info "Deploying Gunicorn and REST Service Configuration files..."
# rest service ports are set as runtime properties in nginx/scripts/create.sh
deploy_blueprint_resource "${CONFIG_REL_PATH}/cloudify-rest.conf" "${REST_SERVICE_HOME}/cloudify-rest.conf"

ctx logger info "Setting the REST Security settings"
ctx logger info "Manager security properties is: $(ctx target node properties security)"
sec_settings=$(ctx -j target node properties security)
echo $sec_settings | sudo tee "${REST_SERVICE_HOME}/rest-security.conf"

configure_systemd_service "restservice"
