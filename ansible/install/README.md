# Install

Playbooks for installing/configuring associated infrastructure with Performance Analysis and Testing of CFME/Miq. Also playbooks for automating importing new CFME/Miq appliances into RHEVM.  **This is mostly a WIP.**

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
2. Monitoring Host - Hosts Carbon/Graphite/Grafana for system performance monitoring
3. Results/Logs Host - Hosts an ELK stack to review testing results and log files from appliances

### monitorhost.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/monitorhost.yml
```
Creates a monitoring host machine by installing graphite/grafana and collectd on a single machine.  This basically combines graphite.yml, grafana.yml, grafana-dashboards.yml in a single playbook.

#### graphite.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/graphite.yml
```
Installs graphite onto a machine designated as a graphite host.

#### grafana.yml
```
[root@perf ansible]# ansible-playbook -i hosts.local install/grafana.yml
```
Installs grafana onto a machine designated as a grafana host.  Usually this is co-located with the Graphite host.

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
