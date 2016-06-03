"""Functions pertaining to determining version of appliance."""
from utils.ssh import SSHClient


# Potentially could use improvement in the future
def get_current_version():
    ssh_client = SSHClient()
    exit_status, current_version = ssh_client.run_command('cat /var/www/miq/vmdb/VERSION')
    return current_version.strip()
