"""Rest API interactions to the appliance for provider and VM configuration/testing."""
from utils.conf import cfme_performance
from utils.log import logger
import time
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


def get_all_host_ids():
    """Returns an integer list of host ID's via the Rest API"""
    logger.debug('Retrieving the list of host ids')

    host_ids = []
    host_response = requests.get(
        url="https://" + cfme_performance['appliance']['ipaddress'] + "/api/hosts",
        auth=(cfme_performance['appliance']['rest_api']['username'],
              cfme_performance['appliance']['rest_api']['password']),
        verify=False
    )

    host_json = host_response.json()
    host_urls = host_json['resources']
    for url in host_urls:
        last_slash = url['href'].rfind('/')
        host_ids.append(int(url['href'][last_slash + 1:]))
    return host_ids


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
    vmid_details['vendor'] = str(vmid_json['vendor'])
    vmid_details['host_id'] = str(vmid_json['host_id'])
    vmid_details['power_state'] = str(vmid_json['power_state'])
    return vmid_details


def add_provider(provider):
    """Adds Provider via the Rest API."""
    logger.vdebug('Adding Provider: {}, Type: {}'.format(provider['name'], provider['type']))

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
    elif 'password_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['password_credentials']['username'],
            "password": provider['password_credentials']['password'],
            "auth_type": "password"
        })
    elif 'bearer_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['bearer_credentials']['username'],
            "password": provider['bearer_credentials']['password'],
            "auth_type": "bearer"
        })
    elif 'amqp_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['amqp_credentials']['username'],
            "password": provider['amqp_credentials']['password'],
            "auth_type": "amqp"
        })
    elif 'ssh_keypair_credentials' in provider:
        data_dict['resources'][0]['credentials'].append({
            "userid": provider['ssh_keypair_credentials']['username'],
            "password": provider['ssh_keypair_credentials']['password'],
            "auth_type": "ssh_keypair"
        })

    # elif '<OTHER_AUTH_TYPES>' in cfme_performance[provider]:
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

    logger.vdebug('Added Provider: {}, Response: {}'.format(provider['name'], response))


def add_providers(providers):
    start_add_provider_time = time.time()

    for provider in providers:
        add_provider(cfme_performance['providers'][provider])

    add_provider_time = time.time() - start_add_provider_time
    logger.debug('refresh_providers took: {}s'.format(round(add_provider_time, 2)))


def add_host_credentials(provider):
    logger.vdebug('Added host credentials to provider: {}'.format(provider['name']))

    # REVIEW: does this work?
    data_dict = {
        "action": "edit",
        "resources": [{
            "credentials": {  # TODO: figure out what to call this
                "userid": provider['host_credentials']['username'],
                "password": provider['host_credentials']['password']
            }
        }]
    }

    json_data = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    for host in get_all_host_ids():
        response = requests.post("https://" + appliance + "/api/hosts" + str(host),
                                 data=json_data,
                                 auth=(cfme_performance['appliance']['rest_api']['username'],
                                       cfme_performance['appliance']['rest_api']['password']),
                                 verify=False,
                                 headers={"content-type": "application/json"},
                                 allow_redirects=False)

        if response.status_code != 200:
            logger.debug(response.text)

    logger.vdebug('Added host credentials, Response: {}'.format(response))


def scan_provider_vm(vm_id):
    logger.vdebug('Scanning VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "scan"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Scanned VM: {}, Response: {}'.format(vm_id, response))


def refresh_provider(provider_id):
    logger.vdebug('Refreshing Provider with id: {}'.format(provider_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/providers/" + str(provider_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Refreshed Provider: {}, Response: {}'.format(provider_id, response))


def refresh_providers(provider_ids):
    start_refresh_provider_time = time.time()
    for provider in provider_ids:
        refresh_provider(provider)
    refresh_provider_time = time.time() - start_refresh_provider_time
    logger.debug('refresh_providers took: {}s'.format(round(refresh_provider_time, 2)))


def refresh_provider_host(provider):
    logger.debug('TODO: Initiate Provider Host Refresh')


def refresh_provider_vm(vm_id):
    logger.vdebug('Refreshing VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "refresh"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Refreshed VM: {}, Response: {}'.format(vm_id, response))


def refresh_provider_vms(vm_ids):
    start_refresh_vms_time = time.time()
    for vm in vm_ids:
        refresh_provider_vm(vm)
    refresh_vms_time = time.time() - start_refresh_vms_time
    logger.debug('refresh_provider_vms took: {}s'.format(round(refresh_vms_time, 2)))


def shutdown_vm_guest(vm_id):
    logger.vdebug('Shutting down guest VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "shutdown_guest"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Shutdown guest VM: {}, Response: {}'.format(vm_id, response))


def reboot_vm_guest(vm_id):
    logger.vdebug('Rebooting guest VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "reboot_guest"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Rebooted guest VM: {}, Response: {}'.format(vm_id, response))


def start_vm(vm_id):
    logger.vdebug('Starting VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "start"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Started VM: {}, Response: {}'.format(vm_id, response))


def stop_vm(vm_id):
    logger.vdebug('Stopping VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "stop"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Stopped VM: {}, Response: {}'.format(vm_id, response))


def suspend_vm(vm_id):
    logger.vdebug('Suspending VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "suspend"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Suspended VM: {}, Response: {}'.format(vm_id, response))


def reset_vm(vm_id):
    logger.vdebug('Reseting VM with ID: {}'.format(vm_id))

    appliance = cfme_performance['appliance']['ip_address']
    response = requests.post("https://" + appliance + "/api/vms/" + str(vm_id),
                             data=json.dumps({"action": "reset"}),
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Reset VM: {}, Response: {}'.format(vm_id, response))
