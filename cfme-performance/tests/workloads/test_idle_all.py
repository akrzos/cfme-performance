"""Runs Idle Workload by resetting appliance and enabling all roles with no providers."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_all_idle
from utils.appliance import set_server_roles_workload_all_idle
from utils.conf import cfme_performance
from utils.log import logger
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
import time


def test_idle_all(request):
    """Runs an appliance at idle with specific roles turned on for specific amount of time. Memory
    Monitor creates graphs and summary at the end of the scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()

    clean_appliance(ssh_client)

    monitor_thread = SmemMemoryMonitor(SSHClient(), 'workload-idle', 'all-roles',
        'Idle with All Roles On', get_server_roles_all_idle(separator=', '), 'No Providers')

    def cleanup_workload(from_ts):
        starttime = time.time()
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.signal = False
        monitor_thread.join()
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(from_ts))

    monitor_thread.start()

    # Allow evmserverd to be started before attempting to reload/adjust the vmdb yml
    time.sleep(45)
    set_server_roles_workload_all_idle(ssh_client)

    s_time = cfme_performance['workloads']['test_idle_all']['total_time']
    logger.info('Idling appliance for {}s'.format(s_time))
    time.sleep(s_time)

    logger.info('Test Ending...')
