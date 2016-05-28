from utils.ssh import SSHClient


# Will definitely need improvement in the future
def get_current_version():
    ssh_client = SSHClient()
    exit_status, current_version = ssh_client.run_command('cat /var/www/miq/vmdb/VERSION')
    return current_version.strip()
