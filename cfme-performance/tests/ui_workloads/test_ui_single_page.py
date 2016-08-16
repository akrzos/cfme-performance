"""Workload to stress WebUI with python requests."""
from utils.appliance import get_server_roles_ui_workload
from utils.conf import cfme_performance
from utils.grafana import get_scenario_dashboard_urls
from utils.log import logger
from utils.smem_memory_monitor import add_workload_quantifiers
from utils.smem_memory_monitor import SmemMemoryMonitor
from utils.ssh import SSHClient
from utils.workloads import get_ui_single_page_scenarios
import pytest
import re
import requests
import time


@pytest.mark.usefixtures('set_server_roles_ui_workload_session', 'generate_version_files')
@pytest.mark.parametrize('scenario', get_ui_single_page_scenarios())
def test_ui_single_page(request, scenario):
    """UI Workload to initiate navigations on the WebUI to dashboard and to various major pages."""
    from_ts = int(time.time() * 1000)
    logger.debug('Scenario: {}'.format(scenario['name']))

    scenario_data = {'appliance_ip': cfme_performance['appliance']['ip_address'],
        'appliance_name': cfme_performance['appliance']['appliance_name'],
        'test_dir': 'ui-workload-single-page',
        'test_name': 'UI-single-page'.format(),
        'appliance_roles': get_server_roles_ui_workload(),
        'scenario': scenario}
    quantifiers = {}
    monitor_thread = SmemMemoryMonitor(SSHClient(), scenario_data)

    def cleanup_workload(scenario, from_ts, quantifiers):
        starttime = time.time()
        to_ts = int(starttime * 1000)
        g_urls = get_scenario_dashboard_urls(scenario, from_ts, to_ts)
        logger.debug('Started cleaning up monitoring thread.')
        monitor_thread.grafana_urls = g_urls
        monitor_thread.signal = False
        monitor_thread.join()
        add_workload_quantifiers(quantifiers, scenario_data)
        timediff = time.time() - starttime
        logger.info('Finished cleaning up monitoring thread in {}'.format(timediff))
    request.addfinalizer(lambda: cleanup_workload(scenario, from_ts, quantifiers))

    monitor_thread.start()

    cfme_ip = cfme_performance['appliance']['ip_address']
    ui_user = cfme_performance['appliance']['web_ui']['username']
    ui_password = cfme_performance['appliance']['web_ui']['password']
    request_number = scenario['requests']
    quantifiers['number of requests'] = request_number
    request_page = scenario['request_page']

    url = 'https://{}/'.format(cfme_ip)
    credentials = {'user_name': ui_user, 'user_password': ui_password}
    headers = {'Accept': 'text/html'}

    with requests.Session() as session:
        response = session.get(url, verify=False, allow_redirects=False, headers=headers)
        found = re.findall(
            r'\<meta\s*content\=\"([0-9a-zA-Z+\/]*\=\=)\"\s*name\=\"csrf\-token\"\s*\/\>',
            response.text)

        if found:
            headers['X-CSRF-Token'] = found[0]
        else:
            logger.error('CSRF Token not found.')

        response = session.post('{}{}'.format(url, 'dashboard/authenticate'), params=credentials,
            verify=False, allow_redirects=False, headers=headers)

        # Get a protected page now:
        requests_start = time.time()
        for i in range(request_number):
            response = session.get('{}{}'.format(url, 'dashboard/show'), verify=False,
                headers=headers)
            response = session.get('{}{}'.format(url, request_page), verify=False, headers=headers)

        requests_time = time.time() - requests_start
    logger.info('created {} Requests in {}s'.format(request_number, round(requests_time, 2)))
    logger.info('Test Ending...')
