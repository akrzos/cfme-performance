from utils.conf import cfme_performance
from utils.log import logger
import json
import requests


def get_all_provider_ids():
    """Returns an integer list of provider ID's via the Rest API"""
    logger.debug('Retrieving the list of provider ids')

    provider_ids = []
    provider_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/providers",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    provider_json = provider_response.json()
    provider_urls = provider_json['resources']
    for url in provider_urls:
        last_slash = url['href'].rfind('/')
        provider_ids.append(int(url['href'][last_slash + 1:]))

    return provider_ids


def get_all_vm_ids():
    """Returns an integer list of vm ID's via the Rest API"""
    logger.debug('Retrieving the list of vm ids')

    vm_ids = []
    vm_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/vms",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    vm_json = vm_response.json()
    vm_urls = vm_json['resources']
    for url in vm_urls:
        last_slash = url['href'].rfind('/')
        vm_ids.append(int(url['href'][last_slash + 1:]))

    return vm_ids


def get_provider_details(provider_id):
    """Returns the id, name, and type associated with the provider_id"""
    logger.debug('Retrieving the provider details for ID: {}'.format(provider_id))

    id_details = {}
    id_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] +
            "/api/providers/" + str(provider_id),
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )
    id_json = id_response.json()

    id_details['name'] = str(id_json['name'])
    id_details['type'] = str(id_json['type'])

    return id_details


def get_vm_details(vm_id):
    """Returns the id, name, and type associated with the vm_id"""
    logger.debug('Retrieving the vm details for ID: {}'.format(vm_id))

    vmid_details = {}
    vmid_response = requests.get(
        url="https://" + cfme_performance['appliance']['ip_address'] +
            "/api/vms/" + str(vm_id),
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )
    vmid_json = vmid_response.json()

    vmid_details['name'] = str(vmid_json['name'])
    vmid_details['type'] = str(vmid_json['type'])

    return vmid_details


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

    if 'metrics_credentials' in provider:
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


def refresh_provider(provider_id):
    logger.debug('Refreshing Provider with id: {}'.format(provider_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers/" + str(provider_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('Refreshed Provider: {}, Response: {}'.format(provider_id, response))


def refresh_provider_host(provider):
    logger.debug('TODO: Initiate Provider Host Refresh')


def refresh_provider_vm(vm_id):
    logger.debug('Refreshing VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    logger.debug('Refreshed VM: {}, Response: {}'.format(vm_id, response))
