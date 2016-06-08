"""Runs Refresh Workload by adding specified providers, and refreshing a specified number, waiting,
then repeating for specified length of time."""
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
def test_refresh_rapid(request, scenario):
    """Refreshes a specified number of providers then waits for a specific amount of time.
    Memory Monitor creates graphs and summary at the end of the scenario."""
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
    logger.info('Sleeping for refresh: {}s'.format(scenario['refresh_sleep_time']))
    time.sleep(scenario['refresh_sleep_time'])

    def get_refresh_ids(start_id, size, list):
        """"""
        refresh_list = []
        if start_id != 0:
            list = list[start_id:] + list[0:start_id]
        if size > len(list):
                fullTimes = size / len(list)
                leftOver = size % len(list)
        else:
                fullTimes = 0
                leftOver = size
        i = 0
        while i < fullTimes:
                refresh_list = refresh_list + list
                i += 1
        refresh_list = refresh_list + list[0:leftOver]
        return {'new_start_id': (start_id + size) % len(list), 'ids_to_refresh': refresh_list}

    start_id = 0
    refresh_size = scenario['refresh_size']
    id_list = get_all_provider_ids()

    # Variable amount of time for refresh workload
    total_time = scenario['total_time']
    start_time = time.time()
    wait_time = scenario['wait_time']
    elapsed_time = 0

    while (elapsed_time < total_time):
        elapsed_time = time.time() - start_time
        time_left = abs(total_time - elapsed_time)
        logger.info('Time elapsed: {}/{}'.format(round(elapsed_time, 2), total_time))
        refresh_dict = get_refresh_ids(start_id, refresh_size, id_list)
        start_id = refresh_dict['new_start_id']
        refresh_providers(refresh_dict['ids_to_refresh'])

        if time_left < wait_time:
            time.sleep(time_left)
        else:
            time.sleep(wait_time)

    logger.info('Test Ending...')
