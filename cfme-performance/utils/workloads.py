"""Functions for workloads."""
from utils.conf import cfme_performance


def get_capacity_and_utilization_scenarios():
    if (cfme_performance['workloads']['test_cap_and_util']['scenarios'] and
            len(cfme_performance['workloads']['test_cap_and_util']['scenarios']) > 0):
        return cfme_performance['workloads']['test_cap_and_util']['scenarios']
    return []


def get_provisioning_scenarios():
    if(cfme_performance['workloads']['test_provisioning']['scenarios'] and
            len(cfme_performance['workloads']['test_provisioning']['scenarios']) > 0):
        return cfme_performance['workloads']['test_provisioning']['scenarios']
    return []


def get_refresh_providers_scenarios():
    if (cfme_performance['workloads']['test_refresh_providers']['scenarios'] and
            len(cfme_performance['workloads']['test_refresh_providers']['scenarios']) > 0):
        return cfme_performance['workloads']['test_refresh_providers']['scenarios']
    return []


def get_refresh_vms_scenarios():
    if (cfme_performance['workloads']['test_refresh_vms']['scenarios'] and
            len(cfme_performance['workloads']['test_refresh_vms']['scenarios']) > 0):
        return cfme_performance['workloads']['test_refresh_vms']['scenarios']
    return []


def get_smartstate_analysis_scenarios():
    if(cfme_performance['workloads']['test_smartstate']['scenarios'] and
            len(cfme_performance['workloads']['test_smartstate']['scenarios']) > 0):
        return cfme_performance['workloads']['test_smartstate']['scenarios']
    return []
