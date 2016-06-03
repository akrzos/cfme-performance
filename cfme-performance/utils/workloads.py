"""Functions for workloads."""
from utils.conf import cfme_performance


def get_capacity_and_utilization_scenarios():
    if (cfme_performance['workloads']['test_cap_and_util']['scenarios'] and
            len(cfme_performance['workloads']['test_cap_and_util']['scenarios']) > 0):
        return cfme_performance['workloads']['test_cap_and_util']['scenarios']
    return []
