# Cleanup

Playbooks that help cleanup CFME/Miq appliances for Performance Analysis and Testing.

**Table of Contents**
========
- [Playbooks](#playbooks)
  - [clean-logs.yml](#clean-logsyml)
  - [clean-logs-restart.yml](#clean-logs-restartyml)
  - [reset-database.yml](#reset-databaseyml)

# Playbooks

## clean-logs.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/clean-logs.yml
```
Deletes all rotated log files in /var/www/miq/vmdb/log/ and /var/www/miq/vmdb/log/apache/. Truncates any log files in those directories.  **Does not restart evmserverd**

## clean-logs-restart.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/clean-logs-restart.yml
```
Stops all CFME/Miq Services, then deletes all log files in /var/www/miq/vmdb/log/ and /var/www/miq/vmdb/log/apache/.  Restarts services at conclusion of cleaning up log files.

## reset-database.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/reset-database.yml
```
Stops evmserverd, drops file system cache, restarts Postgres, removes replication, resets database, seeds database, deletes all files in /var/www/miq/vmdb/run/httpd/, and starts services.  Briefly stops collectd in addition to evmserverd due to the Postgres connection from the collectd configuration.

## reset-all.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/reset-all.yml
```
Stops evmserverd and all CFME/Miq Services, drops file system cache, restarts Postgres, removes replication, resets database, seeds database, deletes all log files in /var/www/miq/vmdb/log/ and /var/www/miq/vmdb/log/apache/ and deletes all files in /var/www/miq/vmdb/run/httpd/, and then starts services.  Briefly stops collectd in addition to evmserverd due to the Postgres connection from the collectd configuration.
