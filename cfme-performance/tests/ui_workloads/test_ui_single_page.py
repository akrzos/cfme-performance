"""Workload to stress WebUI with python requests."""
from requests.auth import HTTPBasicAuth
from utils.appliance import clean_appliance
from utils.appliance import get_server_roles_ui_workload_single_page
from utils.appliance import set_server_roles_ui_workload_single_page
from utils.appliance import wait_for_miq_server_workers_started
from utils.conf import cfme_performance
from utils.grafana import get_scenario_dashboard_url
from utils.log import logger
from utils.providers import add_providers
from utils.smem_memory_monitor import add_workload_quantifiers
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_ui_single_page_scenarios
import pytest
import re
import requests
import time


# @pytest.mark.usefixtures('generate_version_files', 'change_forgery_protection')
@pytest.mark.parametrize('scenario', get_ui_single_page_scenarios())
def test_ui_single_page(request, scenario):
    """UI Workload to initiate navigations on the WebUI from python"""
    from_ts = int(time.time() * 1000)
    ssh_client = SSHClient()
    logger.debug('Scenario: {}'.format(scenario['name']))

    scenario_data = {'appliance_ip': cfme_performance['appliance']['ip_address'],
        'appliance_name': cfme_performance['appliance']['appliance_name'],
        'test_dir': 'ui-workload-single-page',
        'test_name': 'UI-single-page'.format(),
        'appliance_roles': '',
        'scenario': scenario}
    quantifiers = {}
    if scenario['clean_appliance']:
        scenario_data['appliance_roles'] = get_server_roles_ui_workload_single_page(separator=', ')
    monitor_thread = SmemMemoryMonitor(SSHClient(), scenario_data)

    def cleanup_workload(scenario, from_ts, quantifiers):
        starttime = time.time()
        to_ts = int(starttime * 1000)
        g_url = get_scenario_dashboard_url(scenario, from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_url = g_url
        monitor_thread.signal = False
        monitor_thread.join()
        add_workload_quantifiers(quantifiers, scenario_data)
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(scenario, from_ts, quantifiers))

    if scenario['clean_appliance']:
        wait_for_miq_server_workers_started(poll_interval=2)
        clean_appliance(ssh_client)

    monitor_thread.start()
    if scenario['clean_appliance']:
        set_server_roles_ui_workload_single_page(ssh_client)
    add_providers(scenario['providers'])

    cfme_ip = cfme_performance['appliance']['ip_address']
    ui_user = cfme_performance['appliance']['web_ui']['username']
    ui_password = cfme_performance['appliance']['web_ui']['password']
    request_number = scenario['requests']
    quantifiers['number of requests'] = request_number
    request_page = scenario['request_page']

    url = "https://{}/".format(cfme_ip)
    credentials = {"user_name": ui_user, "user_password": ui_password}
    header = {"Accept": "text/html"}

    with requests.Session() as session:
        response = session.get("{}{}".format(url, "api/auth?requester_type=ui"),
            auth=HTTPBasicAuth(ui_user, ui_password), verify=False,
            allow_redirects=False, headers=header)

        response = session.get(url, verify=False, allow_redirects=False, headers=header)
        found = re.findall(
            r'\<meta\s*content\=\"([0-9a-zA-Z+\/]*\=\=)\"\s*name\=\"csrf\-token\"\s*\/\>',
            response.text)

        if found:
            header['X-CSRF-Token'] = found[0]

        response = session.post("{}{}".format(url, "dashboard/authenticate"),
            params=credentials,
            verify=False,
            allow_redirects=False,
            headers=header)

        logger.info("response: {}".format(response))
        logger.info("response headers: {}".format(response.headers))
        logger.info("response request headers: {}".format(response.request.headers))

        # Get a protected page now:
        requests_start = time.time()
        for i in range(request_number):
            response = session.get("{}{}".format(url, "dashboard/show"), verify=False, headers=header)
            response = session.get("{}{}".format(url, request_page), verify=False, headers=header)

        requests_time = time.time() - requests_start
    logger.info('created {} Requests in {}s'.format(request_number, requests_time))

    total_time = time.time() - from_ts
    logger.info('Workload ran in {}s'.format(total_time))
    logger.info('Test Ending...')
