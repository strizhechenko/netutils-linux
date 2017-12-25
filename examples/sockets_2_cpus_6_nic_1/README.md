Fixed: placed eth2 interrupts on local CPU socket (it was bound to the first NUMA-node).

# lscpu

``` shell
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                12
On-line CPU(s) list:   0-11
Thread(s) per core:    1
Core(s) per socket:    6
Socket(s):             2
NUMA node(s):          2
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 44
Model name:            Intel(R) Xeon(R) CPU           X5650  @ 2.67GHz
Stepping:              2
CPU MHz:               2666.618
BogoMIPS:              5333.24
Virtualization:        VT-x
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              12288K
NUMA node0 CPU(s):     0,2,4,6,8,10
NUMA node1 CPU(s):     1,3,5,7,9,11
```

``` shell
# The following is the parsable format, which can be fed to other
# programs. Each different item in every column has an unique ID
# starting from zero.
# CPU,Core,Socket,Node,,L1d,L1i,L2,L3
0,0,0,0,,0,0,0,0
1,1,1,1,,1,1,1,1
2,2,0,0,,2,2,2,0
3,3,1,1,,3,3,3,1
4,4,0,0,,4,4,4,0
5,5,1,1,,5,5,5,1
6,6,0,0,,6,6,6,0
7,7,1,1,,7,7,7,1
8,8,0,0,,8,8,8,0
9,9,1,1,,9,9,9,1
10,10,0,0,,10,10,10,0
11,11,1,1,,11,11,11,1
```

# ethtool

``` shell

## eth2

driver: mlx4_en
version: 4.0-2.0.0 (28 Mar 2017)
firmware-version: 2.40.7000
bus-info: 0000:07:00.0
supports-statistics: yes
supports-test: yes
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: yes

Ring parameters for eth2:
Pre-set maximums:
RX:		8192
RX Mini:	0
RX Jumbo:	0
TX:		8192
Current hardware settings:
RX:		1024
RX Mini:	0
RX Jumbo:	0
TX:		512

Channel parameters for eth2:
Pre-set maximums:
RX:		128
TX:		32
Other:		0
Combined:	0
Current hardware settings:
RX:		8
TX:		12
Other:		0
Combined:	0
```

# before and after

## before tuning:

```
# /proc/interrupts
                                                                                                     
  CPU0    CPU1   CPU2    CPU3   CPU4    CPU5   CPU6    CPU7   CPU8    CPU9   CPU10   CPU11           
                                                                                                     
     0   39788      0       0      0       0      0       0      0       0       0       0   eth2-0  
     0       0      0   35308      0       0      0       0      0       0       0       0   eth2-6  
     0       0      0       0      0   36691      0       0      0       0       0       0   eth2-1  
     0       0      0       0      0       0      0   37903      0       0       0       0   eth2-7  
     0       0      0       0      0       0      0       0      0   36788       0       0   eth2-2  
     0       0      0       0      0       0      0       0      0       0       0   38183   eth2-3  
     0   35795      0       0      0       0      0       0      0       0       0       0   eth2-4  
     0       0      0   37120      0       0      0       0      0       0       0       0   eth2-5  
                                                                                                     
# Load per cpu:
                                                                                                         
  CPU     Interrupts   NET RX   NET TX    total   dropped   time_squeeze   cpu_collision   received_rps  
                                                                                                         
  CPU0           138       56        0        4         0              0               0              0  
  CPU1         75615    68834        0   117870         0             12               0              0  
  CPU2            50        0        1        0         0              0               0              0  
  CPU3         72483    65768        0   115188         0             10               0              0  
  CPU4             0        0        0        0         0              0               0              0  
  CPU5         36719    36761        0    51724         0              0               0              0  
  CPU6             0        0        0        0         0              0               0              0  
  CPU7         37921    37960        0    54119         0              0               0              0  
  CPU8             3        0        0        0         0              0               0              0  
  CPU9         36820    36913        0    52525         0              0               0              0  
  CPU10            0        0        0        0         0              0               0              0  
  CPU11        38197    38212        0    54086         0              0               0              0  
                                                                                                         
# Network devices
                                                                                                                                             
  Device   rx-packets   rx-mbits   rx-errors   dropped   missed   fifo   length   overrun   crc   frame   tx-packets   tx-mbits   tx-errors  
                                                                                                                                             
  lo                0          0           0         0        0      0        0         0     0       0            0          0           0  
  eth0              4          0           0         0        0      0        0         0     0       0           59          0           0  
  eth1              0          0           0         0        0      0        0         0     0       0            0          0           0  
  eth2         426665       1836           0         0        0      0        0         0     0       0            0          0           0  
  br0               0          0           0         0        0      0        0         0     0       0            0          0           0 
```

## commands

Replace this example with command you've run on your server and delete this line.

``` shell
# eth2 just receiving traffic
rss-ladder eth2
```

output:

```
- distribute interrupts of eth2 (-) on socket 0
WARNING: some CPUs process multiple queues, consider reduce queue count for this network device
  - eth2: irq 61 eth2-0 -> 0
  - eth2: irq 62 eth2-6 -> 2
  - eth2: irq 63 eth2-1 -> 4
  - eth2: irq 64 eth2-7 -> 6
  - eth2: irq 65 eth2-2 -> 8
  - eth2: irq 67 eth2-3 -> 10
  - eth2: irq 69 eth2-4 -> 0
  - eth2: irq 71 eth2-5 -> 2
```

## after tuning:

```
# /proc/interrupts
                                                                                                     
   CPU0   CPU1    CPU2   CPU3    CPU4   CPU5    CPU6   CPU7    CPU8   CPU9   CPU10   CPU11           
                                                                                                     
  28395      0       0      0       0      0       0      0       0      0       0       0   eth2-0  
      0      0   29015      0       0      0       0      0       0      0       0       0   eth2-6  
      0      0       0      0   32643      0       0      0       0      0       0       0   eth2-1  
      0      0       0      0       0      0   31650      0       0      0       0       0   eth2-7  
      0      0       0      0       0      0       0      0   33703      0       0       0   eth2-2  
      0      0       0      0       0      0       0      0       0      0   30403       0   eth2-3  
  28913      0       0      0       0      0       0      0       0      0       0       0   eth2-4  
      0      0   28803      0       0      0       0      0       0      0       0       0   eth2-5  
                                                                                                     
# Load per cpu:
                                                                                                         
  CPU     Interrupts   NET RX   NET TX    total   dropped   time_squeeze   cpu_collision   received_rps  
                                                                                                         
  CPU0         57405    49956        0   109900         0              0               0              0  
  CPU1            51        0        0        0         0              0               0              0  
  CPU2         57862    47750        0   120323         0              0               0              0  
  CPU3            25        0        0        0         0              0               0              0  
  CPU4         32673    32536        0    61218         0              0               0              0  
  CPU5            43        0        0        0         0              0               0              0  
  CPU6         31656    31534        0    55204         0              0               0              0  
  CPU7             3        0        0        0         0              0               0              0  
  CPU8         33732    33578        0    62053         0              0               0              0  
  CPU9             1        0        0        0         0              0               0              0  
  CPU10        30418    30295        0    55098         0              0               0              0  
  CPU11            4        0        0        0         0              0               0              0  
                                                                                                         
# Network devices
                                                                                                                                             
  Device   rx-packets   rx-mbits   rx-errors   dropped   missed   fifo   length   overrun   crc   frame   tx-packets   tx-mbits   tx-errors  
                                                                                                                                             
  lo                0          0           0         0        0      0        0         0     0       0            0          0           0  
  eth0              6          0           0         0        0      0        0         0     0       0           41          0           0  
  eth1              0          0           0         0        0      0        0         0     0       0            0          0           0  
  eth2         444408       1907           0         0        0      0        0         0     0       0            0          0           0  
  br0               0          0           0         0        0      0        0         0     0       0            0          0           0  
```
