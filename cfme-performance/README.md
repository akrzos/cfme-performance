# cfme-performance - Python Testing Framework

Originally the workloads and benchmarks started as a fork of [RedHatQE/cfme_tests](https://github.com/RedHatQE/cfme_tests) maintained by Alex Krzos however the growing need to have workloads run rapidly, deterministically and easily has come to the need for a separate repository.  The goal of this testing framework is to quickly measure performance, add providers, run a workload, and reset appliances back to a clean state.  The original workloads and benchmarks have a hard requirement of editing multiple yaml files and maintaining an instance of selenium.  The only external requirement for this repo is that of having a provider to test against. (A must have for any testing of ManageIQ and CFME)

For more in-depth analysis you need a "MonitorHost" or a all-in-one Performance Monitored appliance.  Implementing either of those two options gives you a many more measurements and graphs through Grafana of the system performance and potentially application performance metrics (via statsd) of a CFME or ManageIQ appliance.

**Table of Contents**
========
- [Layout of Performance Testing Code](#layout-of-performance-testing-code)
- [Installation](#installation)
- [Configuration/Setup](#configuration/setup)
- [Workloads](#workloads)
- [Running Workloads](#running-workloads)
  - [Running All Workloads](#running-all-workloads)
  - [Running Specific Workloads](#running-specific-workloads)
- [Analysis](#analysis)

## Layout of Performance Testing Code

1. conf - Contains YAML configuration file for testing
2. log - Contains test framework logs
3. results - Contains results from Workloads
4. tests - Contains Workloads
5. utils - Tools and libraries used to facilitate Workloads

## Installation
Please see [Installing for Testing](../README.md#installing-for-testing)

## Configuration/Setup
In order to run tests properly against CFME/ManageIQ, you will need to create and edit conf/cfme_performance.local.yml conf/cfme_performance.yml is provided as a template.
```shell
# cp conf/cfme_performance.yml conf/cfme_performance.local.yml
# vi conf/cfme_performance.local.yml  # Add an appliance and providers
```

## Workloads:

There are two main types of workloads:
* UI Workloads
* Backend Workloads (Known just as workloads)

These are the current (backend) workloads:

* Idle
* Refresh Providers
* Refresh VMs
* Capacity and Utilization
* Capacity and Utilization with Replication (pglogical and rubyrep)
* SmartState Analysis (Scans VMs)
* Provisioning

Each workload can take a list of providers(Except Idle) and a total_time parameter to adjust how long the appliance is stressed with the workload. Each workload has parameters that can adjust the behavior of the workload. (See the default/example configuration file cfme_performance.yml for example workloads and required parameters for each workload - scenario)  This can lead to many variations of the workloads through the use of scenarios.

## Running Workloads
### Running All Workloads/Tests
```shell
# py.test --verbose tests/
```

### Running All UI Workloads
```shell
# py.test --verbose tests/ui_workloads/
```

### Running All Backend Workloads
```shell
# py.test --verbose tests/workloads/
```

### Running Specific Workload(s)
```shell
# py.test --verbose tests/(ui_workloads/workloads)/(workload_to_run).py
```
*Specify the exact path to the workload to be run*

## Analysis
When workloads complete, view the `results/` directory for workload output and check Grafana for system metrics while workload was run.
