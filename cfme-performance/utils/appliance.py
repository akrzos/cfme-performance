from utils.ssh import SSHClient
from utils.log import logger
from textwrap import dedent
import yaml

yaml_loader = dedent("""\
new_conf = YAML::load(File.open('/tmp/vmdb.yml'))
new_conf_symbol = new_conf.deep_symbolize_keys.to_yaml
result = VMDB::Config.save_file(new_conf_symbol)
if result != true
  exit 255
end""")

roles56_all = ['automate', 'database_operations', 'database_synchronization', 'ems_inventory',
    'ems_metrics_collector', 'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations',
    'event', 'git_owner', 'notifier', 'reporting', 'rhn_mirror', 'scheduler', 'smartproxy',
    'smartstate', 'user_interface', 'web_services', 'websocket']

roles56_default = ['automate', 'database_operations', 'ems_inventory', 'ems_operations', 'event',
    'reporting', 'scheduler', 'smartstate', 'user_interface', 'web_services', 'websocket']

roles56_idle = ['automate', 'database_operations', 'database_synchronization', 'ems_inventory',
    'ems_metrics_collector', 'ems_metrics_coordinator', 'ems_metrics_processor', 'ems_operations',
    'event', 'notifier', 'reporting', 'rhn_mirror', 'scheduler', 'smartproxy', 'smartstate',
    'user_interface', 'web_services']


def clean_appliance(ssh_client):
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


def get_server_roles_all_idle(separator=','):
    return separator.join(roles56_all)


def get_server_roles_default_idle(separator=','):
    return separator.join(roles56_default)


def get_server_roles_idle(separator=','):
    return separator.join(roles56_idle)


def set_server_roles_workload_all_idle(ssh_client):
    """Turns on all server roles used for all idle workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_all_idle()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_idle(ssh_client):
    """Turns on all server roles except for git owner and websocket used for idle workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = get_server_roles_idle()
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_cap_and_util(ssh_client):
    """Sets server roles used for all C&U workloads."""
    yaml = get_vmdb_yaml_config('vmdb')
    yaml['server']['role'] = ('automate,database_operations,ems_inventory,ems_metrics_collector'
        ',ems_metrics_coordinator,ems_metrics_processor,ems_operations,event,notifier,reporting'
        ',scheduler,user_interface,web_services')
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_smartstate(ssh_client):
    """Sets server roles for Smartstate workload."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = ('automate,database_operations,ems_inventory,ems_operations,event'
        ',notifier,reporting,scheduler,smartproxy,smartstate,user_interface,web_services')
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_provisioning(ssh_client):
    """Sets server roles for Provisioning workload."""
    yaml = get_vmdb_yaml_config('vmdb')
    yaml['server']['role'] = ('automate,database_operations,ems_inventory,ems_operations,event'
        ',notifier,reporting,scheduler,user_interface,web_services')
    set_vmdb_yaml_config(ssh_client, yaml)


def set_server_roles_workload_all(ssh_client):
    """Turns on all server roles used for all workload memory measurement benchmark. Does not turn
    on datbase_synchronization role."""
    yaml = get_vmdb_yaml_config(ssh_client)
    yaml['server']['role'] = ('automate,database_operations,ems_inventory,ems_metrics_collector'
        ',ems_metrics_coordinator,ems_metrics_processor,ems_operations,event,notifier,reporting'
        ',rhn_mirror,scheduler,smartproxy,smartstate,user_interface,web_services')
    set_vmdb_yaml_config(ssh_client, yaml)
