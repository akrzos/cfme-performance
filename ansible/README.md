# Ansible Playbooks for cfme-performance

A collection of playbooks for Performance Analysis and Testing of CFME/Miq appliances.

**Table of Contents**
========
- [Layout](#layout)
 - [SSH Config File](#ssh-config-file)
 - [Inventory File](#inventory-file)
 - [Group_vars all.yml](#group_vars-allyml)
- [Playbook Directories](#playbook-directories)
 - [Install](#install)
 - [Configure](#configure)
 - [Workloads](#workloads) - WIP
 - [Cleanup](#cleanup)

# Layout
The playbooks are broken up into several directories to organize them.  They all depend on several files which must be setup correctly before running the playbooks.  Those files are ssh-config.local, hosts.local, and group_vars/all.local.yml  Templates of these files are provided: ssh-config.local.template, hosts.local.template, and group_vars/all.yml

## SSH Config File

Your ssh-config.local file informs ssh how to connect to a specified host. Your inventory file should map to your ssh config file.  The ansible.cfg file informs ansible to use your ssh-config.local file to correctly map a host in the inventory to what ssh is configured to connect to.

[Example ssh-config File](ssh-config.local.template)

## Inventory File

Again, make sure each entry in the ssh-config file maps to a host listed in your ansible inventory file.  See templates for mapping.

[Example Inventory File](hosts.local.template)

## Group_vars all.yml

The ansible vars file is located in group_vars/all.yml.  It can be copied and then edited to parameters which match your environment.  This allows you to make overrides to defaults in the all.yml file without introducing them as git changes.  Each playbook will override default variables by including group_vars/all.local.yml last.  This also gives you the option to only add the variables you want to override to your local vars file.

Example group_vars/all.local.yml
```
---
########################################
# Monitor Host Configuration
########################################
# Carbon/Graphite:
carbon_host: 11.22.33.44


###############################
# CFME 2nd interface ip address
###############################
# Map inventory to ip addresses
ip_addresses:
  CF-R0000-DB-Benchmark-5540:
    ipaddr: 172.16.10.10
    netmask: 255.255.255.0
  CF-R0000-DB-Workload-5540-Patched:
    ipaddr: 172.16.10.11
    netmask: 255.255.255.0
  CF-R0000-DB-Workload-5540:
    ipaddr: 172.16.10.12
    netmask: 255.255.255.0
  CF-R0000-DB-Benchmark-5605:
    ipaddr: 172.16.10.13
    netmask: 255.255.255.0
  CF-R0000-DB-Workload-5605:
    ipaddr: 172.16.10.14
    netmask: 255.255.255.0


###############################
# Repos
###############################
repos:
  rhel7:
    baseurl: http://download.cfme-performance.com/repos/RHEL-7/7.2/Server/$basearch/os/
  rhel7z:
    baseurl: http://download.cfme-performance.com/repos/rhel-7.2-z-candidate/x86_64/
  rhscl7:
    baseurl: http://download.cfme-performance.com/repos/RHSCL-2.0-RHEL-6-Alpha-1.8/compose/Server/x86_64/os/
  rhel7_optional:
    baseurl: http://download.cfme-performance.com/repos/RHEL-7/7.2/Server-optional/$basearch/os/

```

# Playbook Directories

## Install
These playbooks are for installing the infrastructure for Performance Analysis and Testing.  They will also serve to automate bringing new builds into the infrastructure for testing.

## Configure
These playbooks automate the setup of a CFME/Miq appliances post deployment.  Essentially, they are responsible to automate taking a cleanly deployed template and turn it into an online CFME/Miq appliance.  They also handle installing any additional performance analysis tooling such as collectd.

## Workloads
**WIP** - These playbooks will automate adding a provider, configuring roles, and configuring advanced settings on the appliance.  It will also include some basic workloads such as queuing a refresh, provisioning, smart state analysis, etc...

## Cleanup
These playbooks can be used to clean up the log files on an appliance (To prevent log directories from filling up).  Also the database can be reset on an appliance to return it to a clean state.
