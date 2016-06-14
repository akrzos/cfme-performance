"""Runs Refresh Workload by adding specified providers, refreshing the providers, waiting, then
repeating for specified length of time."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_refresh_providers
from utils.appliance import set_server_roles_workload_refresh_providers
from utils.appliance import wait_for_miq_server_ready
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
from utils.providers import get_all_provider_ids
from utils.providers import refresh_providers
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_refresh_providers_scenarios
import time
import pytest


@pytest.mark.parametrize('scenario', get_refresh_providers_scenarios())
def test_refresh_providers(request, scenario):
    """Refreshes providers then waits for a specific amount of time. Memory Monitor creates graphs
    and summary at the end of the scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))

    clean_appliance(ssh_client)

    monitor_thread = SmemMemoryMonitor(SSHClient(), 'workload-refresh-providers', scenario['name'],
    'refresh-providers', get_server_roles_workload_refresh_providers(separator=','),
    ', '.join(scenario['providers']))

    def cleanup_workload(scenario, from_ts):
        start_time = time.time()
        to_ts = int(start_time * 1000)
        g_url = get_scenario_dashboard_url(scenario, from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_url = g_url
        monitor_thread.signal = False
        monitor_thread.join()
        timediff = time.time() - start_time
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(scenario, from_ts))

    monitor_thread.start()

    wait_for_miq_server_ready(poll_interval=2)
    set_server_roles_workload_refresh_providers(ssh_client)
    add_providers(scenario['providers'])
    id_list = get_all_provider_ids()

    # Variable amount of time for refresh workload
    total_time = scenario['total_time']
    start_time = time.time()
    time_between_refresh = scenario['time_between_refresh']
    elapsed_time = 0

    while (elapsed_time < total_time):
        elapsed_time = time.time() - start_time
        time_left = abs(total_time - elapsed_time)
        logger.info('Time elapsed: {}/{}'.format(round(elapsed_time, 2), total_time))
        start_refresh_time = time.time()
        refresh_providers(id_list)
        refresh_time = time.time() - start_refresh_time

        if refresh_time > time_between_refresh:
            logger.warning('refresh_time: {} is longer than time_between_refresh'.format(refresh_time))

        if time_left < time_between_refresh:
            time.sleep(time_left)
        else:
            time.sleep(time_between_refresh)

    logger.info('Test Ending...')
