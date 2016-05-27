from utils.ssh import SSHClient
from utils.log import logger


def clean_appliance():
    ssh_client = SSHClient()
    ssh_client.run_command('service evmserverd stop')
    ssh_client.run_command('sync; sync; echo 3 > /proc/sys/vm/drop_caches')
    ssh_client.run_command('service collectd stop')
    ssh_client.run_command('service {}-postgresql restart'.format(db.scl_name()))
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
