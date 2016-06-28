# Ansible Playbooks for cfme-performance

A collection of playbooks for Performance Analysis and Testing of CFME/ManageIQ appliances.

**Table of Contents**
========
- [Layout](#layout)
 - [SSH Config File](#ssh-config-file---ssh-configlocal)
 - [Inventory File](#inventory-file---hostslocal)
 - [Group_vars all.yml](#group_vars---alllocalyml)
- [Playbook Directories](#playbook-directories)
 - [Install](#install)
 - [Configure](#configure)
 - [Workloads](#workloads) - WIP
 - [Cleanup](#cleanup)

# Layout
The playbooks are broken up into several directories to organize them.  They all depend on several files which must be setup correctly before running the playbooks.  Those files are ssh-config.local, hosts.local, and group_vars/all.local.yml  Templates of these files are provided: ssh-config.local.template, hosts.local.template, and group_vars/all.yml

To begin using the playbooks copy the templates and edit your copies as follows:

```
[root@perf ansible]# cp ssh-config.local.template ssh-config.local
[root@perf ansible]# cp hosts.local.template hosts.local
[root@perf ansible]# cp group_vars/all.yml group_vars/all.local.yml
```

Now edit each of the 3 files starting with ssh-config.local, then hosts.local and lastly group_vars/all.local.yml

## SSH Config File - ssh-config.local

Your ssh-config.local file informs ssh how to connect to a specified host via a name (Rather than DNS).  Note that the contents in the template is just an example, you must at a minimum adjust the ip address to map to your appliance. Your inventory file (hosts.local) must map to your ssh config file.  The ansible.cfg file informs ansible to use your ssh-config.local file to correctly map a host in the inventory to what ssh is configured to connect to.

[Example ssh-config File](ssh-config.local.template)

## Inventory File - hosts.local

Again, make sure each entry in the ssh-config.local file maps to a host listed in your ansible inventory file (hosts.local).  See templates for mapping.  Appliances that run a database should be placed under "[cfme-vmdb]".  Appliances that only host workers and connect to an external database should be placed under "[cfme-worker]".  Appliances that you want to deploy All-In-One Performance Monitoring should be placed under "[cfme-all-in-one]".  As you are working you can "comment" out appliances (via "#" in front of the name) as needed to make sure playbooks are only applied against the expected appliances.

[Example Inventory File](hosts.local.template)

## Group_vars - all.local.yml

The ansible vars file is located in group_vars/all.yml.  It should be copied and then edited to parameters which match your environment.  This allows you to make overrides to defaults in the all.yml file without introducing them as git changes.  Each playbook will override default variables by including group_vars/all.local.yml last.  This also gives you the option to only add the variables you want to override to your local vars file.

Example group_vars/all.local.yml
```
---
########################################
# Monitor Host Configuration
########################################
# Carbon/Graphite:
carbon_host: 11.22.33.44


###############################
# CFME Configuration items
###############################
# Per appliance settings:
appliances:
  # Typically cfme-vmdb appliance configuration:
  inventory_hostname1:
    interfaces:
      - name: eth1
        ipaddr: 172.16.10.10
        netmask: 255.255.255.0
    use_separate_vmdb_disk: true
    vmdb_region: 0
    vmdb_disk: /dev/vdb
    vmdb_password: smartvm
    run_collectd: true
    run_statsd: false
  # Appliance that will take a database dump
  inventory_hostname2:
    dbdump: dump1
    interfaces:
      - name: eth1
        ipaddr: 172.16.10.10
        netmask: 255.255.255.0
    use_separate_vmdb_disk: true
    vmdb_region: 0
    vmdb_disk: /dev/vdb
    vmdb_password: smartvm
    run_collectd: true
    run_statsd: false
  # Appliance with different region
  inventory_hostname3:
    interfaces: []
    use_separate_vmdb_disk: true
    vmdb_region: 99
    vmdb_disk: /dev/vdb
    vmdb_password: smartvm
    run_collectd: true
    run_statsd: false


###############################
# Database Dumps
###############################
# Maps the name of the database dump to its http accessible location
db_dumps:
  dump1: http://download.example.com/dbdumps/dump.r0000.cpgd
  dump2: http://download.example.com/dbdumps/dump.r0001.dmp


###############################
# Repos
###############################
repos:
  rhel6:
    baseurl: http://download.example.com/repos/RHEL-6/6.7/Server/$basearch/os/
  rhel6z:
    baseurl: http://download.example.com/repos/RHEL-6.8-20160414.0/6.8/Server/$basearch/os
  rhscl6:
    baseurl: http://download.example.com/repos/RHSCL-2.0-RHEL-6-Alpha-1.8/compose/Server/$basearch/os/
  rhel6_optional:
    baseurl: http://download.example.com/repos/RHEL-6/6.7/Server/optional/$basearch/os/
  rhel7:
    baseurl: http://download.example.com/repos/RHEL-7/7.2/Server/$basearch/os/
  rhel7z:
    baseurl: http://download.example.com/repos/rhel-7.2-z-candidate/$basearch/
  rhscl7:
    baseurl: http://download.example.com/repos/RHSCL-2.0-RHEL-6-Alpha-1.8/compose/Server/$basearch/os/
  rhel7_optional:
    baseurl: http://download.example.com/repos/RHEL-7/7.2/Server-optional/$basearch/os/

```
Each entry under appliances must match an entry in your ansible inventory file (hosts.local) as the ansible variable `inventory_hostname` is used to determine if the configuration is setup for that specific appliance.  Since using ip addresses would be less than ideal, I use an ssh config file (ssh-config.local) to address each machine as a name.  That inventory name is also used for the hostname to make it easy to identify what appliance you have ssh-ed to.

# Playbook Directories

## Install
These playbooks are for installing the infrastructure for Performance Analysis and Testing.  They will also serve to automate bringing new builds into the infrastructure for testing.

## Configure
These playbooks automate the setup of a CFME/ManageIQ appliances post deployment.  Essentially, they are responsible to automate taking a cleanly deployed template and turn it into an online CFME/ManageIQ appliance.  They also handle installing any additional performance analysis tooling such as collectd.

## Workloads
**WIP** - These playbooks will automate adding a provider, configuring roles, and configuring advanced settings on the appliance.  It will also include some basic workloads such as queuing a refresh, provisioning, smart state analysis, etc...

## Cleanup
These playbooks can be used to clean up the log files on an appliance (To prevent log directories from filling up).  Also the database can be reset on an appliance to return it to a clean state.
