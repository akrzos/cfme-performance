"""Runs SmartState Analysis Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_smartstate
from utils.appliance import install_vddk
from utils.appliance import set_server_roles_workload_smartstate
from utils.appliance import wait_for_miq_server_ready
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
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
    # TODO: Set appliance host/relationship (RHEVM)
    # TODO: Implement Smart state analysis workload here

    logger.info('Test Ending...')
