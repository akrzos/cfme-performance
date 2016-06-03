# cfme-performance - Python Testing Framework

Originally the workloads and benchmarks started as a fork of [RedHatQE/cfme_tests](https://github.com/RedHatQE/cfme_tests) maintained by Alex Krzos however the growing need to have workloads and benchmarks run rapidly, deterministically and easily has come to the need for a separate branch.  The goal of this testing framework is to allow one to quickly measure performance, add providers, run a workload, run a benchmark, and reset their appliance back to a clean state.  The original workloads and benchmarks have a hard requirement of editing multiple yaml files and maintaining an instance of selenium.  The only external requirement for this repo is that of having a provider to test against. (A must have for any testing of ManageIQ and CFME)

# Layout of Performance Testing Code

1. conf - Contains YAML configuration file for testing
2. log - Contains test framework logs
3. results - Contains results from Workloads/Benchmarks/Tests
4. tests - Contains Workloads/Benchmarks/Tests
5. utils - Tools and libraries used to facilitate Workloads/Benchmarks/Tests
