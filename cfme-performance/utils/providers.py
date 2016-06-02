from utils.conf import cfme_performance
from utils.log import logger
import json
import requests


def add_provider(provider):
    """Adds Provider via the Rest API."""
    logger.debug('Adding Provider: {}, Type: {}'.format(provider['name'], provider['type']))

    data_dict = {
        "action": "create",
        "resources": [{
            "name": provider['name'],
            "type": provider['type'],
            "hostname": provider['ip_address'],
            "credentials": [{
                "userid": provider['credentials']['username'],
                "password": provider['credentials']['password']
            }]
        }]
    }

    if 'metrics credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['metrics_credentials']['username'],
            "password": provider['metrics_credentials']['password'],
            "auth_type": "metrics"
        })

    # else if '<OTHER_AUTH_TYPES>' in cfme_performance[provider]:
    #     # TODO implement for other appropriate auth_types

    json_data = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers",
                             data=json_data,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('Added Provider: {}, Response: {}'.format(provider['name'], response))


def add_providers(providers):
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])


def refresh_provider(provider):
    logger.debug('TODO: Initiate Provider Refresh')

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers/" + ID,  # TODO find out ID
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('Refreshed Provider: {}, Response: {}'.format(provider['name'], response))


def refresh_provider_host(provider):
    logger.debug('TODO: Initiate Provider Host Refresh')


def refresh_provider_vm(provider):
    logger.debug('TODO: Initiate Provider VM Refresh')

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/",
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('The response for refreshing Provider VM: {} is: {}'
    .format(provider['name'], response.json()))
