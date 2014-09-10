3ware-check
===========

3ware-check is a Python script-wrapper for checking 3ware RAID disks status

There is a similar tool in the (great) [HWRaid](http://hwraid.le-vert.net/wiki/DebianPackages) website. But sadly, if I'm not wrong, it can't get interesting data like drive's **Reallocated Sectors**... That's why I decided to write my own wrapper.

## Download and Run
```bash
$ wget https://github.com/xezpeleta/3ware-check/raw/master/3wcheck.py
$ chmod 755 3wcheck.py
$ ./3wcheck.py
```

Output example:
```
CRITICAL: Drive p2 - Reallocated Sectors: 182
```

## Check multiple servers

If you need to check multiple servers, you may [use this Ansible integration script](https://github.com/xezpeleta/my-ansible-playbooks/tree/master/check-raid-status)

Example:
```bash
./run.sh
srv-11: WARNING: Drive p3 - Reallocated Sectors: 1
srv-06: UNKNOWN: RAID not compatible
srv-03.: OK
srv-14: ERROR: 3ware hardware not detected
srv-16: ERROR: 3ware hardware not detected
srv-01: UNKNOWN: RAID not compatible
srv-12: CRITICAL: Drive p2 - Reallocated Sectors: 182

*** ERROR ***
srv-13: Request failed
*** DOWN ***
srv-09: SSH encountered an unknown error during the connection. We recommend you re-run the command using -vvvv, which will enable SSH debugging output to help diagnose the issue
```
