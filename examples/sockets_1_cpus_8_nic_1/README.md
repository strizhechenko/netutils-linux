Well we've got a: NetXen Incorporated NX3031 Multifunction 1/10-Gigabit Server Adapter (rev 42)

It has 4 RSS queues, but only one seems to be working:

```
# cat /proc/interrupts | grep eth4
 45: 1540180896          0          0          0          0          0          0          0  IR-PCI-MSI-edge      eth4[0]
 46:          0          0          0          0          0          0          0          0  IR-PCI-MSI-edge      eth4[1]
 47:          0          0          0          0          0          0          0          0  IR-PCI-MSI-edge      eth4[2]
 48:          0          0          0          0          0          0          0          0  IR-PCI-MSI-edge      eth4[3]
```

And what's with RPS?

```
# ls /sys/class/net/eth4/queues/
rx-0  tx-0
```

# lscpu

``` shell
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                8
On-line CPU(s) list:   0-7
Thread(s) per core:    2
Core(s) per socket:    4
Socket(s):             1
NUMA node(s):          1
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 60
Model name:            Intel(R) Xeon(R) CPU E3-1230 v3 @ 3.30GHz
Stepping:              3
CPU MHz:               3292.534
BogoMIPS:              6585.06
Virtualization:        VT-x
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              8192K
NUMA node0 CPU(s):     0-7
```

``` shell
# The following is the parsable format, which can be fed to other
# programs. Each different item in every column has an unique ID
# starting from zero.
# CPU,Core,Socket,Node,,L1d,L1i,L2,L3
0,0,0,0,,0,0,0,0
1,1,0,0,,1,1,1,0
2,2,0,0,,2,2,2,0
3,3,0,0,,3,3,3,0
4,0,0,0,,0,0,0,0
5,1,0,0,,1,1,1,0
6,2,0,0,,2,2,2,0
7,3,0,0,,3,3,3,0
```

# ethtool

## eth4

``` shell
driver: netxen_nic
version: 4.0.82
firmware-version: 4.0.588
bus-info: 0000:01:00.1
supports-statistics: yes
supports-test: yes
supports-eeprom-access: yes
supports-register-dump: yes
supports-priv-flags: no

Ring parameters for eth4:
Pre-set maximums:
RX:		8192
RX Mini:	0
RX Jumbo:	1024
TX:		1024
Current hardware settings:
RX:		4096
RX Mini:	0
RX Jumbo:	1024
TX:		1024

Channel parameters for eth4:
Cannot get device channel parameters
: Operation not supported
```

## commands

Replace this example with command you've run on your server and delete this line.

``` shell
# eth4 just receiving traffic
rx-buffers-increase eth0
# despite of having 4 RSS queues only 1 queue really works.
# CPU0 will do receive packets and write them into memory
# CPU1..CPU7 will do all the hardlifting and packet processing.
autorps eth4 -c 1 2 3 4 5 6 7
```
