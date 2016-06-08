"""Appliance specific settings and functions."""
from utils.log import logger
from utils.ssh import SSHTail
from textwrap import dedent
import time
import yaml

yaml_loader = dedent("""\
new_conf = YAML::load(File.open('/tmp/vmdb.yml'))
new_conf_symbol = new_conf.deep_symbolize_keys.to_yaml
result = VMDB::Config.save_file(new_conf_symbol)
if result != true
  exit 255
end""")

roles56_default = ['automate', 'database_operations', 'ems_inventory', 'ems_operations', 'event',
    'reporting', 'scheduler', 'smartstate', 'user_interface', 'web_services', 'websocket']

roles56_idle = ['automate', 'database_operations', 'database_synchronization', 'ems_inventory',
    'ems_metrics_collector', 'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations',
    'event', 'notifier', 'reporting', 'rhn_mirror', 'scheduler', 'smartproxy', 'smartstate',
    'user_interface', 'web_services']

roles56_all = ['automate', 'database_operations', 'database_synchronization', 'ems_inventory',
    'ems_metrics_collector', 'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations',
    'event', 'git_owner', 'notifier', 'reporting', 'rhn_mirror', 'scheduler', 'smartproxy',
    'smartstate', 'user_interface', 'web_services', 'websocket']

roles56_cap_and_util = ['automate', 'database_operations', 'ems_inventory', 'ems_metrics_collector',
    'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations', 'event', 'notifier',
    'reporting', 'scheduler', 'user_interface', 'web_services']

# TODO: set the roles
roles56_refresh_providers = ['automate', 'database_operations', 'ems_inventory', 'ems_operations',
    'event', 'reporting', 'scheduler', 'smartstate', 'user_interface', 'web_services', 'websocket']

# TODO: set the roles
roles56_refresh_vms = ['automate', 'database_operations', 'ems_inventory', 'ems_operations',
    'event', 'reporting', 'scheduler', 'smartstate', 'user_interface', 'web_services', 'websocket']

roles56_smartstate = ['automate', 'database_operations', 'ems_inventory', 'ems_operations', 'event',
    'notifier', 'reporting', 'scheduler', 'smartproxy', 'smartstate', 'user_interface',
    'web_services']

roles56_provisioning = ['automate', 'database_operations', 'ems_inventory', 'ems_operations',
    'event', 'notifier', 'reporting', 'scheduler', 'user_interface', 'web_services']

roles56_workload_all = ['automate', 'database_operations', 'ems_inventory', 'ems_metrics_collector',
    'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations', 'event', 'notifier',
    'reporting', 'rhn_mirror', 'scheduler', 'smartproxy', 'smartstate', 'user_interface',
    'web_services']


def clean_appliance(ssh_client):
    starttime = time.time()
    ssh_client.run_command('service evmserverd stop')
    ssh_client.run_command('sync; sync; echo 3 > /proc/sys/vm/drop_caches')
    ssh_client.run_command('service collectd stop')
    ssh_client.run_command('service rh-postgresql94-postgresql restart')
    ssh_client.run_rake_command('evm:dbsync:local_uninstall')
    # 5.6 requires DISABLE_DATABASE_ENVIRONMENT_CHECK=1
    ssh_client.run_command(
        'cd /var/www/miq/vmdb;DISABLE_DATABASE_ENVIRONMENT_CHECK=1 bin/rake evm:db:reset')
    ssh_client.run_rake_command('db:seed')
    ssh_client.run_command('service collectd start')
    # Work around for https://bugzilla.redhat.com/show_bug.cgi?id=1337525
    ssh_client.run_command('service httpd stop')
    ssh_client.run_command('rm -rf /run/httpd/*')
    ssh_client.run_command('service evmserverd start')
    logger.debug('Cleaned appliance in: {}'.format(time.time() - starttime))


def get_vmdb_yaml_config(ssh_client):
    base_data = ssh_client.run_rails_command('puts\(Settings.to_hash.deep_stringify_keys.to_yaml\)')
    if base_data.rc:
        logger.error("Config couldn't be found")
        logger.error(base_data.output)
        raise Exception('Error obtaining vmdb config')
    yaml_data = base_data.output[:base_data.output.find('DEPRE')]
    return yaml.load(yaml_data)


def set_vmdb_yaml_config(ssh_client, yaml_data):
    logger.info('Uploading VMDB yaml Loader')
    ssh_client.run_command('echo "{}" > /tmp/yaml_loader.rb'.format(yaml_loader), log_less=True)
    logger.info('Uploading VMDB Config')
    ssh_client.run_command('echo "{}" > /tmp/vmdb.yml'.format(
        yaml.dump(yaml_data, default_flow_style=False)), log_less=True)
    result = ssh_client.run_rails_command('/tmp/yaml_loader.rb')
    if result.rc:
        raise Exception('Unable to set config')
    else:
        logger.info('Set VMDB Config')


def set_full_refresh_threshold(ssh_client, threshold=100):
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['ems_refresh']['full_refresh_threshold'] = threshold
    set_vmdb_yaml_config(ssh_client, yaml)


def get_server_roles_workload_idle_default(separator=','):
    return separator.join(roles56_default)


def get_server_roles_workload_idle(separator=','):
    return separator.join(roles56_idle)


def get_server_roles_workload_idle_all(separator=','):
    return separator.join(roles56_all)


def get_server_roles_workload_cap_and_util(separator=','):
    return separator.join(roles56_cap_and_util)


def get_server_roles_workload_refresh_providers(separator=','):
    return separator.join(roles56_refresh_providers)


def get_server_roles_workload_refresh_vms(separator=','):
    return separator.join(roles56_refresh_vms)


def get_server_roles_workload_smartstate(separator=','):
    return separator.join(roles56_smartstate)


def get_server_roles_workload_provisioning(separator=','):
    return separator.join(roles56_provisioning)


def get_server_roles_workload_all(separator=','):
    return separator.join(roles56_workload_all)


def set_server_roles_workload_idle(ssh_client):
    """Turns on all server roles except for git owner and websocket used for idle workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_idle()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_idle_all(ssh_client):
    """Turns on all server roles used for idle all workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_idle_all()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_cap_and_util(ssh_client):
    """Sets server roles used for all C&U workloads."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_cap_and_util()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_refresh_providers(ssh_client):
    """Sets server roles used for all refresh_providers workloads."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_refresh_providers()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_refresh_vms(ssh_client):
    """Sets server roles used for all refresh_vms workloads"""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_refresh_vms()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_smartstate(ssh_client):
    """Sets server roles for Smartstate workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_smartstate()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_provisioning(ssh_client):
    """Sets server roles for Provisioning workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_provisioning()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_all(ssh_client):
    """Turns on all server roles used for all workload memory measurement benchmark. Does not turn
    on datbase_synchronization role."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_workload_all()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_cap_and_util_all_via_rails(ssh_client):
    """Turns on Collect for All Clusters and Collect for all Datastores without using the UI."""
    command = ('Metric::Targets.perf_capture_always = {:storage=>true, :host_and_cluster=>true};')
    ssh_client.run_rails_console(command, timeout=None, log_less=True)


def wait_for_miq_server_ready(poll_interval=5):
    """Waits for the CFME to be ready by tailing evm.log for:
    'INFO -- : MIQ(MiqServer#start) Server starting complete'
    Verified works with 5.6 appliances.
    """
    logger.info('Opening /var/www/miq/vmdb/log/evm.log for tail')
    evm_tail = SSHTail('/var/www/miq/vmdb/log/evm.log')
    evm_tail.set_initial_file_end()

    attempts = 0
    detected = False
    max_attempts = 60
    while (not detected and attempts < max_attempts):
        logger.debug('Attempting to detect MIQ Server ready: {}'.format(attempts))
        for line in evm_tail:
            if 'MiqServer#start' in line:
                if 'Server starting complete' in line:
                    logger.info('Detected MIQ Server is ready.')
                    detected = True
                    break
        time.sleep(poll_interval)  # Allow more log lines to accumulate
        attempts += 1
    if not (attempts < max_attempts):
        logger.error('Could not detect MIQ Server ready in 600s.')
    evm_tail.close()
