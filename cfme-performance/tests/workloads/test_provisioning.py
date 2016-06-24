"""Runs Provisioning Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_provisioning
from utils.appliance import set_server_roles_workload_provisioning
from utils.appliance import wait_for_miq_server_ready
from utils.conf import cfme_performance
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
from utils.providers import delete_provisioned_vm
from utils.providers import delete_provisioned_vms
from utils.providers import provision_vm
from utils.providers import get_template_guids
from utils.providers import get_remaining_vms
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_provisioning_scenarios
from itertools import cycle
import time
import pytest


@pytest.mark.parametrize('scenario', get_provisioning_scenarios())
def test_provisioning(request, scenario):
    """Runs through provisioning scenarios using the REST API to
    continously provision a VM for a specified period of time.
    Memory Monitor creates graphs and summary at the end of each scenario."""

    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))

    clean_appliance(ssh_client)

    scenario_data = {'appliance_ip': cfme_performance['appliance']['ip_address'],
        'appliance_name': cfme_performance['appliance']['appliance_name'],
        'test_dir': 'workload-provisioning',
        'test_name': 'Provisioning',
        'appliance_roles': get_server_roles_workload_provisioning(separator=', '),
        'scenario': scenario}
    monitor_thread = SmemMemoryMonitor(SSHClient(), scenario_data)

    provision_order = []

    def cleanup_workload(scenario, from_ts, vms_to_cleanup):
        starttime = time.time()
        to_ts = int(starttime * 1000)
        g_url = get_scenario_dashboard_url(scenario, from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_url = g_url
        monitor_thread.signal = False
        delete_provisioned_vms(vms_to_cleanup)
        monitor_thread.join()
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(scenario, from_ts, provision_order))

    monitor_thread.start()

    wait_for_miq_server_ready(poll_interval=2)
    set_server_roles_workload_provisioning(ssh_client)
    add_providers(scenario['providers'])
    logger.info('Sleeping for Refresh: {}s'.format(scenario['refresh_sleep_time']))
    time.sleep(scenario['refresh_sleep_time'])

    guid_list = get_template_guids(scenario['templates'])
    guid_cycle = cycle(guid_list)
    cleanup_size = scenario['cleanup_size']
    total_time = scenario['total_time']
    time_between_provision = scenario['time_between_provision']
    total_provisioned_vms = 0
    total_deleted_vms = 0
    provisioned_vms = 0
    starttime = time.time()

    while ((time.time() - starttime) < total_time):
        start_provision_time = time.time()

        total_provisioned_vms += 1
        provisioned_vms += 1
        vm_to_provision = '{}-provision-{}'.format(
            time.strftime('%Y%m%d%H%M%S'), str(total_provisioned_vms).zfill(3))
        guid_to_provision = next(guid_cycle)
        provision_order.append([vm_to_provision, guid_to_provision[1]])
        provision_vm(vm_to_provision, guid_to_provision[0], guid_to_provision[1]['vlan_network'])
        if provisioned_vms > cleanup_size * len(scenario['providers']):
            initial_size = len(provision_order)
            delete_provisioned_vm(provision_order)
            provisioned_vms -= (initial_size - len(provision_order))
            total_deleted_vms += (initial_size - len(provision_order))

        iteration_time = time.time()
        provision_time = round(iteration_time - start_provision_time, 2)
        elapsed_time = iteration_time - starttime
        logger.debug('Time to initiate provisioning: {}'.format(provision_time))
        logger.info('{} VMs provisioned so far'.format(total_provisioned_vms))
        logger.info('Time elapsed: {}/{}'.format(round(elapsed_time, 2), total_time))

        if provision_time < time_between_provision:
            wait_diff = time_between_provision - provision_time
            time_remaining = total_time - elapsed_time
            if (time_remaining > 0 and time_remaining < time_between_provision):
                time.sleep(time_remaining)
            elif time_remaining > 0:
                time.sleep(wait_diff)
            else:
                logger.warn('Time to initiate provisioning ({}) exceeded time between '
                    '({})'.format(provision_time, time_between_provision))

    logger.info('Provisioned {} VMs and deleted {} VMs during the scenario. \
        {} VMs were left over, and {} VMs were deleted in the finalizer.'
        .format(total_provisioned_vms, total_deleted_vms, provisioned_vms, len(provision_order)))
    logger.info('The following VMs were left over after the test: {}'.format(get_remaining_vms()))

    logger.info('Test Ending...')
