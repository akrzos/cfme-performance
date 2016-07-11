# All In One Performance Monitored CFME

## What is an all in one performance monitored CFME

An all-in-one performance monitored appliance is a CFME/ManageIQ appliance with Collectd/Statsd/Carbon/Graphite/Grafana running directly on it.  This allows you to view relevant system performance and application performance metrics of CFME in real time with the included dashboards.

This drastically reduces the amount of time required to understand what has occurred and what is occurring on your appliance with respect to hardware and software.

## What is installed

* Collectd - A daemon that gathers metrics according to its configured plugins.
* Statsd - A daemon for collecting metrics and publishing them to Graphite/Carbon.  A monkey patch is applied to ManageIQ code to publish metrics regarding the MiqQueue implementation to expose its utilization.
* Carbon - A daemon that receives metrics and stores them in memory (carbon-cache) and writes them to whisper database files.
* Graphite - A monitoring tool, primarily used for its API to expose data from carbon-cache and the whisper files to a frontend.
* Grafana - A pretty dashboard-ing tool for presentation of time series data.

## How to deploy an all in one performance monitored CFME?

1. Deploy a CFME/ManageIQ appliance
2. Setup additional space for /var/lib/carbon
    1. Add disk from your hypervisor to CFME/ManageIQ appliance, 15GiB is usually enough for the storage schema deployed via this playbook
    2. Partition disk (Depending upon your environment, the disk name can be different):

        ```
        [root@cfme-all-in-one ~]# fdisk /dev/vdc
        Welcome to fdisk (util-linux 2.23.2).

        Changes will remain in memory only, until you decide to write them.
        Be careful before using the write command.

        Device does not contain a recognized partition table
        Building a new DOS disklabel with disk identifier 0x23e359ee.

        Command (m for help): n
        Partition type:
           p   primary (0 primary, 0 extended, 4 free)
           e   extended
        Select (default p): p
        Partition number (1-4, default 1): 1
        First sector (2048-31457279, default 2048):
        Using default value 2048
        Last sector, +sectors or +size{K,M,G} (2048-31457279, default 31457279):
        Using default value 31457279
        Partition 1 of type Linux and of size 15 GiB is set

        Command (m for help): p

        Disk /dev/vdc: 16.1 GB, 16106127360 bytes, 31457280 sectors
        Units = sectors of 1 * 512 = 512 bytes
        Sector size (logical/physical): 512 bytes / 512 bytes
        I/O size (minimum/optimal): 512 bytes / 512 bytes
        Disk label type: dos
        Disk identifier: 0x23e359ee

           Device Boot      Start         End      Blocks   Id  System
        /dev/vdc1            2048    31457279    15727616   83  Linux

        Command (m for help): w
        The partition table has been altered!

        Calling ioctl() to re-read partition table.
        Syncing disks.
        [root@cfme-all-in-one ~]#
        ```

    3. Make a filesystem on the disk (ext4 for RHEL6, xfs for RHEL7)

        ```
        [root@cfme-all-in-one ~]# mkfs.ext4 /dev/vdc1
        ```

        or

        ```
        [root@cfme-all-in-one ~]# mkfs.xfs /dev/vdc1
        ```

    4. Make the /var/lib/carbon directory

        ```
        [root@cfme-all-in-one ~]# mkdir -p /var/lib/carbon
        ```

    5. Add entry to /etc/fstab (Remember ext4 for RHEL6, xfs for RHEL7)

        ```
        /dev/vdc1               /var/lib/carbon         ext4    defaults        0 0
        ```

    6. Mount filesystem

        ```
        [root@cfme-all-in-one ~]# mount -a
        ```

    7. Check for mounted filesystem (CFME 54 or RHEL6)

        ```
        [root@cfme-all-in-one ~]# lsblk
        NAME                     MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
        sr0                       11:0    1 1024M  0 rom
        vda                      252:0    0   40G  0 disk
        ├─vda1                   252:1    0  512M  0 part /boot
        └─vda2                   252:2    0 39.5G  0 part
          ├─VGCFME-LVOS (dm-0)   253:0    0   10G  0 lvm  /
          ├─VGCFME-LVSwap (dm-1) 253:1    0  9.5G  0 lvm  [SWAP]
          ├─VGCFME-LVLog (dm-2)  253:2    0   10G  0 lvm  /var/www/miq/vmdb/log
          └─VGCFME-LVRepo (dm-3) 253:3    0   10G  0 lvm  /repo
        vdb                      252:16   0   10G  0 disk
        vdc                      252:32   0   15G  0 disk
        └─vdc1                   252:33   0   15G  0 part /var/lib/carbon
        ```
        (CFME 55/56 or RHEL7)
        ```
        [root@cfme-all-in-one ~]#  lsblk
        NAME                          MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
        sr0                            11:0    1 1024M  0 rom
        vda                           252:0    0   40G  0 disk
        ├─vda1                        252:1    0  512M  0 part /boot
        └─vda2                        252:2    0 39.5G  0 part
          ├─VG--CFME-lv_os            253:0    0  4.6G  0 lvm  /
          ├─VG--CFME-lv_swap          253:1    0  9.3G  0 lvm  [SWAP]
          ├─VG--CFME-lv_repo          253:2    0   10G  0 lvm  /repo
          ├─VG--CFME-lv_home          253:3    0    1G  0 lvm  /home
          ├─VG--CFME-lv_tmp           253:4    0    1G  0 lvm  /tmp
          ├─VG--CFME-lv_log           253:5    0   10G  0 lvm  /var/www/miq/vmdb/log
          ├─VG--CFME-lv_var_log_audit 253:6    0  512M  0 lvm  /var/log/audit
          ├─VG--CFME-lv_var_log       253:7    0    1G  0 lvm  /var/log
          └─VG--CFME-lv_var           253:8    0    2G  0 lvm  /var
        vdb                           252:16   0   20G  0 disk
        vdc                           252:32   0   15G  0 disk
        └─vdc1                        252:33   0   15G  0 part /var/lib/carbon
        ```

3. Clone cfme-performance (Either locally on your machine or on the CFME appliance)

    ```
    # git clone https://github.com/akrzos/cfme-performance.git
    ```

4. Setup ssh-config.local, hosts.local, and all.local.yml. Examples:

    * ssh-config.local

        ```
        Host CF-R0000-Example-AIO
            Hostname 10.11.22.33
            IdentityFile ~/.ssh/id_rsa
            StrictHostKeyChecking no
            UserKnownHostsFile=/dev/null
        ```

    * hosts.local

        ```
        # CFME-Performance inventory file
        [monitorhost]

        [cfme-vmdb]

        [cfme-worker]

        [cfme-all-in-one]
        CF-R0000-Example-AIO
        ```

    * all.local.yml

        ```
        ---
        appliances:
          CF-R0000-Example-AIO:
            interfaces: []
            use_separate_vmdb_disk: true
            vmdb_region: 0
            vmdb_disk: /dev/vdb
            vmdb_password: smartvm
            run_collectd: true
            run_statsd: true
        ```

5. Run all-in-one playbook

    ```
    # ansible-playbook -i hosts.local configure/all-in-one.yml
    ```

6. Analyze CFME/ManageIQ System/Application Performance in Grafana!
