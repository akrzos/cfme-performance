# Create

Playbooks used to create Virtual Machines and VM Simulators used for CFME Testing. All playbooks are run on the local host, bypassing Ansible's ssh features. hosts.local can be specified, but is not required.

**Table of Contents**
========
- [Playbooks](#playbooks)
  - [create-cfme-appliance.yml](#create-cfme-applianceyml)

# Playbooks

## create-cfme-appliance.yml

```
[root@perf ansible]# ansible-playbook create/create-cfme-appliance.yml
```
Provisions VMs based on configurable settings in all.local.yml. After prvisioning these VMs are ready to have a configure playbook run against them.
