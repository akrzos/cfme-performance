"""Wrap interactions with Grafana or logging Grafana URLs."""
from utils.conf import cfme_performance
from utils.log import logger


def get_scenario_dashboard_url(scenario, from_ts, to_ts, output_to_log=True):
    """Builds the string URL for a Grafana Dashboard if enabled."""
    if cfme_performance['tools']['grafana']['enabled']:
        g_ip = cfme_performance['tools']['grafana']['ip_address']
        g_port = cfme_performance['tools']['grafana']['port']
        appliance_name = cfme_performance['appliance']['appliance_name']
        dashboard_name = cfme_performance['tools']['grafana']['default_dashboard']
        if 'grafana_dashboard' in scenario:
            dashboard_name = scenario['grafana_dashboard']
        grafana_url = 'http://{}:{}/dashboard/db/{}?from={}&to={}&var-Node={}'.format(g_ip, g_port,
            dashboard_name, from_ts, to_ts, appliance_name)
        if output_to_log:
            logger.info('Grafana URL: {}'.format(grafana_url))
        return grafana_url
    else:
        logger.warn('Grafana integration is not enabled')
        return ''


def get_default_dashboard_url(from_ts, to_ts, output_to_log=True):
    """Builds the string URL for a Grafana Dashboard if enabled."""
    if cfme_performance['tools']['grafana']['enabled']:
        g_ip = cfme_performance['tools']['grafana']['ip_address']
        g_port = cfme_performance['tools']['grafana']['port']
        appliance_name = cfme_performance['appliance']['appliance_name']
        dashboard_name = cfme_performance['tools']['grafana']['default_dashboard']
        grafana_url = 'http://{}:{}/dashboard/db/{}?from={}&to={}&var-Node={}'.format(g_ip, g_port,
            dashboard_name, from_ts, to_ts, appliance_name)
        if output_to_log:
            logger.info('Grafana URL: {}'.format(grafana_url))
        return grafana_url
    else:
        logger.warn('Grafana integration is not enabled')
        return ''
