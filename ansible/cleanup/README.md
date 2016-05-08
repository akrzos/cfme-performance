- [Cleanup](#cleanup)
  - [clean-logs.yml](#clean-logs.yml)
  - [delete-logs.yml](#delete-logs.yml)
  - [reset-database.yml](#reset-database.yml)

# Cleanup

A place for playbooks that help cleanup CFME/Miq appliances after Performance testing.

## clean-logs.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/clean-logs.yml
```
Deletes all rotated log files in /var/www/miq/vmdb/log/ and /var/www/miq/vmdb/log/apache/. Truncates any log files in those directories.  **Does not restart evmserverd**

## delete-logs.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/delete-logs.yml
```
Stops all CFME/Miq Services, then deletes all log files in /var/www/miq/vmdb/log/ and /var/www/miq/vmdb/log/apache/.  Restarts services at conclusion of cleaning up log files.

## reset-database.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local cleanup/reset-database.yml
```
Stops evmserverd, drops file system cache, restarts Postgres, removes replication, resets database, seeds database, and starts services.  Briefly stops collectd in addition to evmserverd due to the Postgres connection from the collectd configuration.
