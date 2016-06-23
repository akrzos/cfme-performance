"""REST API interactions to the appliance for provider and VM configuration/testing."""
from utils.conf import cfme_performance
from utils.log import logger
import time
import json
import requests


def get_all_provider_ids():
    """Returns an integer list of provider ID's via the REST API"""
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
    """Returns an integer list of vm ID's via the REST API"""
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
        url="https://" + cfme_performance['appliance']['ip_address'] + "/api/hosts",
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
    """Returns the name, and type associated with the provider_id"""
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
    """Returns the name, type, vendor, host_id, and power_state associated with the vm_id"""
    logger.debug('Retrieving the VM details for ID: {}'.format(vm_id))

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
    if 'host_id' in vmid_json:
        vmid_details['host_id'] = str(vmid_json['host_id'])
    vmid_details['power_state'] = str(vmid_json['power_state'])
    return vmid_details


def get_provider_id(provider_name):
    """"Return the ID associated with the specified provider name"""
    logger.debug('Retrieving the ID for provider: {}'.format(provider_name))
    for provider_id in get_all_provider_ids():
        details = get_provider_details(provider_id)
        if details['name'] == provider_name:
            return provider_id
    return


def get_vm_id(vm_name):
    """"Return the ID associated with the specified VM name"""
    logger.debug('Retrieving the ID for VM: {}'.format(vm_name))
    for vm_id in get_all_vm_ids():
        details = get_vm_details(vm_id)
        if details['name'] == vm_name:
            return vm_id
    return


def add_provider(provider):
    """Adds a provider via the REST API."""
    logger.vdebug('Adding Provider: {}, Type: {}'.format(provider['name'], provider['type']))

    data_dict = {
        "action": "create",
        "resources": [{
            "name": provider['name'],
            "type": provider['type'],
            "credentials": [{
                "userid": provider['credentials']['username'],
                "password": provider['credentials']['password']
            }]
        }]
    }

    if 'ip_address' in provider:
        data_dict['resources'][0]['hostname'] = provider['ip_address']

    if (provider['type'] == 'ManageIQ::Providers::Amazon::CloudManager' or
    provider['type'] == 'ManageIQ::Providers::Google::CloudManager'):
        data_dict['resources'][0]['provider_region'] = provider['provider_region']

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
    """Adds a provider with one request per provider via the REST API."""
    starttime = time.time()
    for provider in providers:
        add_provider(cfme_performance['providers'][provider])
    logger.info('Added Providers in: {}s'.format(round(time.time() - starttime, 2)))


def add_host_credentials(provider):
    """"Adds host credentials to a provider via the REST API"""
    data_dict = {
        "action": "edit",
        "resource": {
            "credentials": {
                "userid": provider['host_credentials']['username'],
                "password": provider['host_credentials']['password']
            }
        }
    }

    json_data = json.dumps(data_dict)
    appliance = cfme_performance['appliance']['ip_address']
    for host in get_all_host_ids():
        response = requests.post("https://" + appliance + "/api/hosts/" + str(host),
                                 data=json_data,
                                 auth=(cfme_performance['appliance']['rest_api']['username'],
                                       cfme_performance['appliance']['rest_api']['password']),
                                 verify=False,
                                 headers={"content-type": "application/json"},
                                 allow_redirects=False)

        if response.status_code != 200:
            logger.debug(response.text)

        print response  # TODO: REMOVE

    logger.debug('Added host credentials, Response: {}'.format(response))


def scan_provider_vm(vm_id):
    """Performs Smart State Analysis on the specified VM via the REST API"""
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

    logger.vdebug('Queued Scan VM: {}, Response: {}'.format(vm_id, response))


def scan_provider_vms(vm_ids):
    """Performs Smart State Analysis on the specified VMs with one request per VM
    via the REST API"""
    starttime = time.time()
    for vm in vm_ids:
        scan_provider_vm(vm)
    logger.vdebug('Queued Scan {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def scan_provider_vms_bulk(vm_ids):
    """Performs Smart State Analysis on the specified VMs with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for vm_id in vm_ids:
        resources.append({
            "href": "https://" + appliance + "/api/vms/" + str(vm_id)
        })

    data_dict = {
        "action": "scan",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/vms/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Queued Scan {} VM(s) in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def refresh_provider(provider_id):
    """Refresh the specified provider via the REST API"""
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

    logger.vdebug('Queued Refresh Provider: {}, Response: {}'.format(provider_id, response))


def refresh_providers(provider_ids):
    """Refresh the specified providers with one request per provider via the REST API"""
    starttime = time.time()
    for provider in provider_ids:
        refresh_provider(provider)
    logger.vdebug('Queued Refresh {} Provider(s) in: {}s'.format(len(provider_ids),
        round(time.time() - starttime, 2)))


def refresh_providers_bulk(provider_ids):
    """Refresh the specified providers with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for provider_id in provider_ids:
        resources.append({
            "href": "https://" + appliance + "/api/providers/" + str(provider_id)
        })

    data_dict = {
        "action": "refresh",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/providers/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.vdebug('Queued Refresh {} Provider(s) in: {}s'.format(len(provider_ids),
        round(time.time() - starttime, 2)))


def refresh_provider_vm(vm_id):
    """Refresh the specified VM via the REST API"""
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
    """Refresh the specified VMs with one request per VM via the REST API"""
    starttime = time.time()
    for vm in vm_ids:
        refresh_provider_vm(vm)
    logger.debug('Queued Refresh {} VMs in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def refresh_provider_vms_bulk(vm_ids):
    """Refresh the specified VMs with one request via the REST API"""
    starttime = time.time()

    appliance = cfme_performance['appliance']['ip_address']
    resources = []
    for vm_id in vm_ids:
        resources.append({
            "href": "https://" + appliance + "/api/vms/" + str(vm_id)
        })

    data_dict = {
        "action": "refresh",
        "resources": resources
    }
    data_json = json.dumps(data_dict)
    response = requests.post("https://" + appliance + "/api/vms/",
                             data=data_json,
                             auth=(cfme_performance['appliance']['rest_api']['username'],
                                   cfme_performance['appliance']['rest_api']['password']),
                             verify=False,
                             headers={"content-type": "application/json"},
                             allow_redirects=False)

    if response.status_code != 200:
        logger.debug(response.text)

    logger.debug('Queued Refresh {} VMs in: {}s'.format(len(vm_ids),
        round(time.time() - starttime, 2)))


def shutdown_vm_guest(vm_id):
    """Shut down the specified VM  via the REST API"""
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
    """Reboot the specified VM  via the REST API"""
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
    """Start the specified VM  via the REST API"""
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
    """Stop the specified VM  via the REST API"""
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
    """Suspend the specified VM  via the REST API"""
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
    """Reset the specified VM via the REST API"""
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
