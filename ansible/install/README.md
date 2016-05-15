# Install

Playbooks for installing/configuring associated infrastructure with Performance Analysis and Testing of CFME/Miq. Also playbooks for automating importing new CFME/Miq appliances into RHEVM.

**Table of Contents**
========
- [Playbooks](#playbooks)
  - [Infrastructure Install Playbooks](#infrastructure-install-playbooks)
    - [monitorhost.yml](#monitorhostyml)
      - [graphite.yml](#graphiteyml)
      - [grafana.yml](#grafanayml)
      - [grafana-dashboards.yml](#grafana-dashboardsyml)
  - [Deployment Playbooks](#deployment-playbooks)
    - [upload-template.yml](#upload-templateyml)

# Playbooks

## Infrastructure Install Playbooks
Three major infrastructure hosts:
1. Workload Driver - Hosts cfme-performance and cfme_tests (perf fork)
2. Monitoring Host - RHEL7 Machine that Hosts Carbon/Graphite/Grafana for system performance monitoring
3. Results/Logs Host - Hosts an ELK stack to review testing results and log files from appliances
All should be built on RHEL7/Centos7

### monitorhost.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/monitorhost.yml
```
Creates a monitoring host machine by installing carbon/graphite/grafana and collectd on a single machine.  This basically combines graphite.yml, grafana.yml, grafana-dashboards.yml in a single playbook.  Before running, create a RHEL 7 machine with large enough disk space in /var/lib/carbon to accommodate the number of CFME/Miq appliances you plan on monitoring. (~5-7GiB per appliance with included CFME collectd configs)

#### graphite.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/graphite.yml
```
Installs carbon/graphite onto a machine designated as a monitor host.

#### grafana.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/grafana.yml
```
Installs grafana onto a machine designated as a monitor host.  Usually this is co-located with the carbon/graphite host.

#### grafana-dashboards.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/grafana-dashboards.yml
```
Uploads dashboards into grafana host.

## Deployment Playbooks

### upload-template.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/upload-template.yml
```
**WIP** to upload new appliance template to RHEVM.
