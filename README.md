# cfme-performance

A WIP repo with the goal to provide end-to-end CFME/Miq performance analysis and testing.

## Major Components

This repo is contains two major components to facilitate its goals:
* [Ansible Playbooks](ansible/)
* [Python Testing Framework](cfme-performance/)

Browse the Ansible folder for more details on the playbooks which automate standing up appliances and installing performance analysis tools.  Browse the cfme-performance folder to explore the pytest driven workloads and benchmarks.

## Installing for testing

```shell
# virtualenv cfme-perf-test
# cd cfme-perf-test
# . bin/activate
# git clone https://github.com/akrzos/cfme-performance.git
# cd cfme-performance
# pip install -Ur requirements.txt
# cp cfme-performance/conf/cfme_performance.yml cfme-performance/conf/cfme_performance.local.yml
# vi cfme-performance/conf/cfme_performance.local.yml  # Add an appliance and providers
# py.test --verbose cfme-performance/tests/workloads/
```

When workloads complete, view `cfme-performance/results` for workload output and check Grafana for system metrics while workload was run.
