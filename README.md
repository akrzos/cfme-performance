# cfme-performance

A WIP repo with the goal to provide end-to-end CFME/Miq Performance Analysis/Testing Framework and tooling.

## Install

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

When workloads complete, view `cfme-performance/results` for workload output and check Grafana for System metrics while workload was run.
