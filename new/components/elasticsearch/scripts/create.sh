#!/bin/bash -e

. $(ctx download-resource "components/utils")
. $(ctx download-resource "components/elasticsearch/scripts/configure_es")


CONFIG_REL_PATH="components/elasticsearch/config"

export ES_JAVA_OPTS=$(ctx node properties es_java_opts)  # (e.g. "-Xmx1024m -Xms1024m")
export ES_HEAP_SIZE=$(ctx node properties es_heap_size)
export ES_HEAP_SIZE=${ES_HEAP_SIZE:-1g}
export ES_CURATOR_RPM_SOURCE_URL=$(ctx node properties es_curator_rpm_source_url)
export ES_SOURCE_URL=$(ctx node properties es_rpm_source_url)  # (e.g. "https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.3.tar.gz")

# this will be used only if elasticsearch-curator is not installed via an rpm
export ES_CURATOR_VERSION="3.2.3"

export ELASTICSEARCH_PORT="9200"
export ELASTICSEARCH_HOME="/opt/elasticsearch"
export ELASTICSEARCH_LOG_PATH="/var/log/cloudify/elasticsearch"
export ELASTICSEARCH_CONF_PATH="/etc/elasticsearch"


ctx logger info "Installing Elasticsearch..."

copy_notice "elasticsearch"
create_dir ${ELASTICSEARCH_HOME}
create_dir ${ELASTICSEARCH_LOG_PATH}

yum_install ${ES_SOURCE_URL}


# we should treat these as templates.
ctx logger info "Setting Elasticsearch Heap size..."
replace "#ES_HEAP_SIZE=2g" "ES_HEAP_SIZE=${ES_HEAP_SIZE}" "/etc/sysconfig/elasticsearch"

if [ ! -z "${ES_JAVA_OPTS}" ]; then
    ctx logger info "Setting additional Java OPTS..."
    replace "#ES_JAVA_OPTS=" "ES_JAVA_OPTS=${ES_JAVA_OPTS}" "/etc/sysconfig/elasticsearch"
fi

ctx logger info "Deploying Elasticsearch Configuration..."
deploy_blueprint_resource "${CONFIG_REL_PATH}/elasticsearch.yml" "${ELASTICSEARCH_CONF_PATH}/elasticsearch.yml"

ctx logger info "Starting Elasticsearch for configuration purposes..."
sudo systemctl enable elasticsearch.service &>/dev/null
sudo systemctl start elasticsearch.service

ctx logger info "Waiting for Elasticsearch to become available..."
wait_for_port "${ELASTICSEARCH_PORT}"

ctx logger info "Configuring Elasticsearch Indices, Mappings, etc..."
# per a function in configure_es
configure_elasticsearch

ctx logger info "Stopping Elasticsearch Service..."
sudo systemctl stop elasticsearch.service

ctx logger info "Installing Elasticsearch Curator..."
if [ -z ${ES_CURATOR_RPM_SOURCE_URL} ]; then
    install_module "elasticsearch-curator==${ES_CURATOR_VERSION}"
else
    yum_install ${ES_CURATOR_RPM_SOURCE_URL}
fi

rotator_script=$(ctx download-resource-and-render components/elasticsearch/scripts/rotate_es_indices)

ctx logger info "Configuring Elasticsearch Index Rotation cronjob for logstash-YYYY.mm.dd index patterns..."
# testable manually by running: sudo run-parts /etc/cron.daily
sudo mv ${rotator_script} /etc/cron.daily/rotate_es_indices
sudo chown -R root:root /etc/cron.daily/rotate_es_indices
sudo chmod +x /etc/cron.daily/rotate_es_indices