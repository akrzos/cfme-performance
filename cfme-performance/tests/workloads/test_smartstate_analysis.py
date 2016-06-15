"""Runs SmartState Analysis Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_smartstate
from utils.appliance import install_vddk
from utils.appliance import set_cfme_server_relationship
from utils.appliance import set_server_roles_workload_smartstate
from utils.appliance import wait_for_miq_server_ready
from utils.conf import cfme_performance
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
from utils.providers import get_all_vm_ids
from utils.providers import get_provider_id
from utils.providers import add_host_credentials
from utils.providers import scan_provider_vms
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_smartstate_analysis_scenarios
import time
import pytest


@pytest.mark.parametrize('scenario', get_smartstate_analysis_scenarios())
def test_workload_smartstate_analysis(request, scenario):
    """Runs through provider based scenarios initiating smart state analysis against VMs, Hosts,
    and Datastores"""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))
    install_vddk(ssh_client)

    clean_appliance(ssh_client)

    monitor_thread = SmemMemoryMonitor(SSHClient(), 'workload-ssa', scenario['name'],
        'SmartState Analysis', get_server_roles_workload_smartstate(separator=', '),
        ', '.join(scenario['providers']))

    def cleanup_workload(scenario, from_ts):
        starttime = time.time()
        to_ts = int(starttime * 1000)
        g_url = get_scenario_dashboard_url(scenario, from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_url = g_url
        monitor_thread.signal = False
        monitor_thread.join()
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(scenario, from_ts))

    monitor_thread.start()

    wait_for_miq_server_ready(poll_interval=2)
    set_server_roles_workload_smartstate(ssh_client)
    add_providers(scenario['providers'])
    logger.info('Sleeping for Refresh: {}s'.format(scenario['refresh_sleep_time']))
    time.sleep(scenario['refresh_sleep_time'])

    # TODO: add credentials to hosts via REST API here (VMware)
    for provider_name in scenario['providers']:
        provider = cfme_performance['providers'][provider_name]
        add_host_credentials(provider)
        if provider['type'] == "ManageIQ::Providers::Redhat::InfraManager":
            set_cfme_server_relationship(ssh_client,
                                         cfme_performance['appliance']['appliance_name'])

    for vm_name in scenario['']
    # TODO: Implement Smart state analysis workload here
    time_between_analyses = scenario['time_between_analysis']
    total_time = scenario['total_time']
    start_time = time.time()
    elapsed_time = 0
    while (elapsed_time < total_time):
        elapsed_time = time.time() - start_time
        time_left = abs(total_time - elapsed_time)
        start_scan_time = time.time()
        scan_provider_vms(get_all_vm_ids())
        scan_time = time.time() - start_scan_time

        if scan_time > time_between_analyses:
            logger.warning('scan_time: {} > time_between_analyses'.format(scan_time))

        if time_left < time_between_analyses - scan_time:
            sleep_time = time_left
        else:
            sleep_time = abs(time_between_analyses - scan_time)
        logger.vdebug('sleeping for {}s between refresh cycles'.format(sleep_time))
        time.sleep(sleep_time)

    logger.info('Test Ending...')
