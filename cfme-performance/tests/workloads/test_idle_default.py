"""Runs Idle Workload by resetting appliance and idling with no providers."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_workload_idle_default
from utils.appliance import wait_for_miq_server_ready
from utils.conf import cfme_performance
from utils.log import logger
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
import time


def test_idle_default(request):
    """Runs an appliance at idle for specific amount of time. Memory Monitor creates graphs and
    summary at the end of the scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()

    clean_appliance(ssh_client)

    monitor_thread = SmemMemoryMonitor(SSHClient(), 'workload-idle', 'default',
        'Idle with Default Roles', get_server_roles_workload_idle_default(separator=', '),
        'No Providers')

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
    # No need to set server roles as we are using the default set of roles

    s_time = cfme_performance['workloads']['test_idle_default']['total_time']
    logger.info('Idling appliance for {}s'.format(s_time))
    time.sleep(s_time)

    logger.info('Test Ending...')
