# cfme-performance

A repo with the goal to provide end-to-end CFME/ManageIQ performance analysis and testing.

## Major Components

This repo is contains two major components to facilitate its goals:
* [Ansible Playbooks](ansible/)
* [Python Testing Framework](cfme-performance/)

Browse the Ansible folder for more details on the playbooks which automate standing up appliances and installing performance analysis tools.  Browse the cfme-performance folder to explore the pytest driven workloads.

## Installing for testing

```shell
# virtualenv cfme-performance
# cd cfme-performance
# . bin/activate
# git clone https://github.com/akrzos/cfme-performance.git
# cd cfme-performance
# pip install -Ur requirements.txt
# cp cfme-performance/conf/cfme_performance.yml cfme-performance/conf/cfme_performance.local.yml
# vi cfme-performance/conf/cfme_performance.local.yml  # Add an appliance and providers
# py.test --verbose cfme-performance/tests/workloads/
```
*Note there is several rpms you may have to install depending on what is already installed in your environment.*

When workloads complete, view `cfme-performance/results` directory for workload output and check Grafana for system metrics while workload was run.

## Workloads:

These are the current workloads:

* Idle (default, no websocket/git_owner roles, all roles)
* Refresh Providers
* Refresh VMs
* Capacity and Utilization
* SmartState Analysis (Scans VMs)
* Provisioning

Each workload(Except Idle) can take a list of providers and a total_time parameter to adjust how long the appliance is stressed with the workload. Each workload has its only parameters that can adjust the behavior of the workload. (See the default configuration file cfme_performance.yml for example workloads and required parameters for each workload - scenario)  This can lead to many variations of the workloads.
