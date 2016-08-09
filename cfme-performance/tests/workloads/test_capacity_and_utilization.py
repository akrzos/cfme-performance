"""Runs Capacity and Utilization Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_cap_and_util
from utils.appliance import set_cap_and_util_all_via_rails
from utils.appliance import set_server_roles_workload_cap_and_util
from utils.appliance import wait_for_miq_server_workers_started
from utils.conf import cfme_performance
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_capacity_and_utilization_scenarios
import time
import pytest


@pytest.mark.usefixtures('generate_version_files')
@pytest.mark.parametrize('scenario', get_capacity_and_utilization_scenarios())
def test_workload_capacity_and_utilization(request, scenario):
    """Runs through provider based scenarios enabling C&U and running for a set period of time.
    Memory Monitor creates graphs and summary at the end of each scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))

    clean_appliance(ssh_client)

    scenario_data = {'appliance_ip': cfme_performance['appliance']['ip_address'],
        'appliance_name': cfme_performance['appliance']['appliance_name'],
        'test_dir': 'workload-cap-and-util',
        'test_name': 'Capacity and Utilization',
        'appliance_roles': get_server_roles_workload_cap_and_util(separator=', '),
        'scenario': scenario}
    monitor_thread = SmemMemoryMonitor(SSHClient(), scenario_data)

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

    wait_for_miq_server_workers_started(poll_interval=2)
    set_server_roles_workload_cap_and_util(ssh_client)
    add_providers(scenario['providers'])
    logger.info('Sleeping for Refresh: {}s'.format(scenario['refresh_sleep_time']))
    time.sleep(scenario['refresh_sleep_time'])
    set_cap_and_util_all_via_rails(ssh_client)

    # Variable amount of time for C&U collections/processing
    total_time = scenario['total_time']
    starttime = time.time()
    elapsed_time = 0
    while (elapsed_time < total_time):
        elapsed_time = time.time() - starttime
        time_left = total_time - elapsed_time
        logger.info('Time elapsed: {}/{}'.format(round(elapsed_time, 2), total_time))
        if (time_left > 0 and time_left < 300):
            time.sleep(time_left)
        elif time_left > 0:
            time.sleep(300)

    logger.info('Test Ending...')
