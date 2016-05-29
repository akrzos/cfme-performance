"""Runs Capacity and Utilization Workload."""
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_default_idle
from utils.conf import cfme_performance
from utils.log import logger
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient

import time
import pytest


@pytest.mark.parametrize('scenario',
    cfme_performance['workloads']['test_cap_and_util']['scenarios'])
def test_workload_capacity_and_utilization(request, scenario):
    """Runs through provider based scenarios enabling C&U and running for a set period of time.
    Memory Monitor creates graphs and summary at the end of each scenario."""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()

    logger.info('Scenario: {}'.format(scenario))

    # TODO: Complete this scenario

    logger.info('Test Ending...')
