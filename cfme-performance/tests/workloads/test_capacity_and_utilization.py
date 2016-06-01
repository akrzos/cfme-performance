"""Runs Capacity and Utilization Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_cap_and_util
from utils.appliance import set_cap_and_util_all_via_rails
from utils.appliance import set_server_roles_workload_cap_and_util
from utils.appliance import wait_for_miq_server_ready
from utils.conf import cfme_performance
from utils.log import logger
from utils.providers import add_providers
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_capacity_and_utilization_scenarios
import time
import pytest


@pytest.mark.parametrize('scenario', get_capacity_and_utilization_scenarios())
def test_workload_capacity_and_utilization(request, scenario):
    """Runs through provider based scenarios enabling C&U and running for a set period of time.
    Memory Monitor creates graphs and summary at the end of each scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))

    clean_appliance(ssh_client)

    monitor_thread = SmemMemoryMonitor(SSHClient(), 'workload-cap-and-util', scenario['name'],
        'Capacity and Utilization', get_server_roles_workload_cap_and_util(separator=', '),
        ', '.join(scenario['providers']))

    def cleanup_workload(from_ts):
        starttime = time.time()
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.signal = False
        monitor_thread.join()
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(from_ts))

    monitor_thread.start()

    wait_for_miq_server_ready(poll_interval=2)
    set_server_roles_workload_cap_and_util(ssh_client)
    add_providers(scenario['providers'])
    logger.info('Sleeping for Refresh: {}s'.format(scenario['refresh_sleep_time']))
    time.sleep(scenario['refresh_sleep_time'])
    set_cap_and_util_all_via_rails(ssh_client)

    # Variable amount of time for C&U collections/processing
    total_time = scenario['total_time']
    starttime = time.time()
    total_waited = 0
    while (total_waited < total_time):
        total_waited = time.time() - starttime
        time_left = abs(total_time - total_waited)
        logger.info('Time waited: {}/{}'.format(round(total_waited, 2), total_time))
        if time_left < 300:
            time.sleep(time_left)
        else:
            time.sleep(300)

    logger.info('Test Ending...')
