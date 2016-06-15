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
from utils.providers import add_host_credentials
from utils.providers import scan_provider_vm
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
    for provider in scenario['providers']:
        add_host_credentials(cfme_performance['providers'][provider])
        if (cfme_performance['providers'][provider]['type'] ==
                "ManageIQ::Providers::Redhat::InfraManager"):
            set_cfme_server_relationship(ssh_client,
                cfme_performance['appliance']['appliance_name'])

    # Variable amount of time for SmartState Analysis workload
    total_time = scenario['total_time']
    starttime = time.time()
    time_between_analyses = scenario['time_between_analyses']

    # TODO Get ids of VMs/Hosts/Datastores to scan from name identifiers in cfme_performance yml

    while ((time.time() - starttime) < total_time):
        start_ssa_time = time.time()
        # TODO loop through list of ids of VMs/Hosts/Datastores to scan here and initiate a scan
        time.sleep(1)  # placeholder
        iteration_time = time.time()

        ssa_time = round(iteration_time - start_ssa_time, 2)
        elapsed_time = iteration_time - starttime
        logger.debug('Time to initiate SmartState Analyses: {}'.format(ssa_time))
        logger.info('Time elapsed: {}/{}'.format(round(elapsed_time, 2), total_time))

        if ssa_time < time_between_analyses:
            wait_diff = time_between_analyses - ssa_time
            time_remaining = total_time - elapsed_time
            if (time_remaining > 0 and time_remaining < time_between_analyses):
                time.sleep(time_remaining)
            elif time_remaining > 0:
                time.sleep(wait_diff)
        else:
            logger.warn('Time to initiate SmartState Analyses ({}) exceeded time between '
                '({})'.format(ssa_time, time_between_analyses))

    logger.info('Test Ending...')
