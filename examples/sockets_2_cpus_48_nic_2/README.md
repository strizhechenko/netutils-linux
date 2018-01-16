# lscpu

``` shell
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                48
On-line CPU(s) list:   0-47
Thread(s) per core:    2
Core(s) per socket:    12
Socket(s):             2
NUMA node(s):          2
Vendor ID:             GenuineIntel
CPU family:            6
Model:                 79
Model name:            Intel(R) Xeon(R) CPU E5-2687W v4 @ 3.00GHz
Stepping:              1
CPU MHz:               2996.512
BogoMIPS:              5992.43
Virtualization:        VT-x
L1d cache:             32K
L1i cache:             32K
L2 cache:              256K
L3 cache:              30720K
NUMA node0 CPU(s):     0-11,24-35
NUMA node1 CPU(s):     12-23,36-47
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
4,4,0,0,,4,4,4,0
5,5,0,0,,5,5,5,0
6,6,0,0,,6,6,6,0
7,7,0,0,,7,7,7,0
8,8,0,0,,8,8,8,0
9,9,0,0,,9,9,9,0
10,10,0,0,,10,10,10,0
11,11,0,0,,11,11,11,0
12,12,1,1,,12,12,12,1
13,13,1,1,,13,13,13,1
14,14,1,1,,14,14,14,1
15,15,1,1,,15,15,15,1
16,16,1,1,,16,16,16,1
17,17,1,1,,17,17,17,1
18,18,1,1,,18,18,18,1
19,19,1,1,,19,19,19,1
20,20,1,1,,20,20,20,1
21,21,1,1,,21,21,21,1
22,22,1,1,,22,22,22,1
23,23,1,1,,23,23,23,1
24,0,0,0,,0,0,0,0
25,1,0,0,,1,1,1,0
26,2,0,0,,2,2,2,0
27,3,0,0,,3,3,3,0
28,4,0,0,,4,4,4,0
29,5,0,0,,5,5,5,0
30,6,0,0,,6,6,6,0
31,7,0,0,,7,7,7,0
32,8,0,0,,8,8,8,0
33,9,0,0,,9,9,9,0
34,10,0,0,,10,10,10,0
35,11,0,0,,11,11,11,0
36,12,1,1,,12,12,12,1
37,13,1,1,,13,13,13,1
38,14,1,1,,14,14,14,1
39,15,1,1,,15,15,15,1
40,16,1,1,,16,16,16,1
41,17,1,1,,17,17,17,1
42,18,1,1,,18,18,18,1
43,19,1,1,,19,19,19,1
44,20,1,1,,20,20,20,1
45,21,1,1,,21,21,21,1
46,22,1,1,,22,22,22,1
47,23,1,1,,23,23,23,1
```

# ethtool

## eth0

``` shell
driver: qlcnic
version: 5.3.59
firmware-version: 4.9.98
bus-info: 0000:05:00.0
supports-statistics: yes
supports-test: yes
supports-eeprom-access: yes
supports-register-dump: yes
supports-priv-flags: no
Ring parameters for eth0:
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

Channel parameters for eth0:
Pre-set maximums:
RX:		8
TX:		8
Other:		0
Combined:	0
Current hardware settings:
RX:		4
TX:		1
Other:		0
Combined:	0
```

## eth1

``` shell
driver: qlcnic
version: 5.3.59
firmware-version: 4.9.98
bus-info: 0000:05:00.1
supports-statistics: yes
supports-test: yes
supports-eeprom-access: yes
supports-register-dump: yes
supports-priv-flags: no
Ring parameters for eth1:
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

Channel parameters for eth1:
Pre-set maximums:
RX:		8
TX:		8
Other:		0
Combined:	0
Current hardware settings:
RX:		4
TX:		1
Other:		0
Combined:	0
```

# before and after

## before tuning:

### /proc/interrupts

```
   CPU0   CPU1   CPU2   CPU3   CPU4   CPU5   CPU6   CPU7   CPU8   CPU9   CPU10   CPU11   CPU12   CPU13   CPU14   CPU15   CPU16   CPU17   CPU18   CPU19   CPU20   CPU21   CPU22   CPU23   CPU24   CPU25   CPU26   CPU27   CPU28   CPU29   CPU30   CPU31   CPU32   CPU33   CPU34   CPU35   CPU36   CPU37   CPU38   CPU39   CPU40   CPU41   CPU42   CPU43   CPU44   CPU45   CPU46   CPU47

   6192      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-0
  11550      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-1
   6694      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-2
   9163      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-tx-0-rx-3
   7100      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-0
   7373      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-1
   9688      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-2
  14055      0      0      0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-tx-0-rx-3
  27066    461    250     68     45     51      4     26     25     33      42      10     491     114      60      18      25      29       5      31      14      12       9       2     378     469     114      60      32      35      23      16       7      28      12      16      62     437     538     107      24      29       9       4      10      23      10      26   interrupts
```

### Load per cpu:

```
  CPU     Interrupts   NET RX   NET TX   total   dropped   time_squeeze   cpu_collision   received_rps

  CPU0         98891    39209    55161   81064         0              1               0              0
  CPU1           479        5        9      14         0              0               0              0
  CPU2           250        3       12       6         0              0               0              0
  CPU3            80        5        9      12         0              0               0              0
  CPU4            45        1        4       2         0              0               0              0
  CPU5            51        0        5       0         0              0               0              0
  CPU6             5        1        2       2         0              0               0              0
  CPU7            26        0        3       0         0              0               0              0
  CPU8            25        1       23       2         0              0               0              0
  CPU9            33        0        2       0         0              0               0              0
  CPU10           42        0       11       0         0              0               0              0
  CPU11           41        0        0       0         0              0               0              0
  CPU12          506        1       46       4         0              0               0              0
  CPU13          131        3       12       6         0              0               0              0
  CPU14           60        0       14       0         0              0               0              0
  CPU15           18        0        0       0         0              0               0              0
  CPU16           25        2        2       4         0              0               0              0
  CPU17           29        0        9       0         0              0               0              0
  CPU18            5        0        0       0         0              0               0              0
  CPU19           31        0        8       0         0              0               0              0
  CPU20           14        0        0       0         0              0               0              0
  CPU21           12        0        6       0         0              0               0              0
  CPU22            9        0        0       0         0              0               0              0
  CPU23            2        0        0       0         0              0               0              0
  CPU24          382       43      234      86         0              0               0              0
  CPU25          482        1       68       2         0              0               0              0
  CPU26          177        0       15       0         0              0               0              0
  CPU27           60        0       12       0         0              0               0              0
  CPU28           51        0       12       0         0              0               0              0
  CPU29           88        0        4       0         0              0               0              0
  CPU30           23        0        0       0         0              0               0              0
  CPU31           16        0        0       0         0              0               0              0
  CPU32            7        0        0       0         0              0               0              0
  CPU33           28        0        6       0         0              0               0              0
  CPU34           28        0        0       0         0              0               0              0
  CPU35           16        0        0       0         0              0               0              0
  CPU36           62        0       10       0         0              0               0              0
  CPU37          473        0        9       0         0              0               0              0
  CPU38          541        0        3       0         0              0               0              0
  CPU39          107        0        0       0         0              0               0              0
  CPU40           24        1        3       2         0              0               0              0
  CPU41           41        1       26       2         0              0               0              0
  CPU42            9        0        0       0         0              0               0              0
  CPU43            4        0        0       0         0              0               0              0
  CPU44           10        0        3       0         0              0               0              0
  CPU45           26        0        0       0         0              0               0              0
  CPU46           10        0        0       0         0              0               0              0
  CPU47           26        0        1       0         0              0               0              0
```

### Network devices

```
  Device      rx-packets   rx-mbits   rx-errors   dropped   missed   fifo   length   overrun   crc   frame    tx-packets    tx-mbits   tx-errors

  lo                1565         17           0         0        0      0        0         0     0       0          1565          17           0
  imq0             29725        122           0         0        0      0        0         0     0       0         29725         122           0
  imq1             55813        476           0         0        0      0        0         0     0       0         56170         480           0
  eth0             33856        131           0         0        0      0        0         0     0       0   12489232215   113189608           0
  eth1             57878        494           0         0        0      0        0         0     0       0    7549411498    21616698           0
  eth6                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth7                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth5                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth4                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.10             40          0           0         0        0      0        0         0     0       0            40           0           0
  eth0.100          6797         51           0         0        0      0        0         0     0       0          9999          61           0
  eth0.101           416          0           0         0        0      0        0         0     0       0           533           5           0
  eth0.102          7086         16           0         0        0      0        0         0     0       0         15150         142           0
  eth0.1022         3499         22           0         0        0      0        0         0     0       0          3374          23           0
  eth0.103          4452          6           0         0        0      0        0         0     0       0          7367          68           0
  eth0.104          6077         27           0         0        0      0        0         0     0       0         10444          90           0
  eth0.105            20          0           0         0        0      0        0         0     0       0            14           0           0
  eth0.106             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.107             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.108             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.109          5401          4           0         0        0      0        0         0     0       0         10808         110           0
  dummy0               0          0           0         0        0      0        0         0     0       0             0           0           0
```

## commands


- eth1 - default route
- eth0 - local network with a lot of vlan


despite qlogic's max queue count is 8 it can't be set to this value.

``` shell
> ethtool -L eth0 rx 8 tx 1
tx unmodified, ignoring
Cannot set device channel parameters: Invalid argument
> ethtool -L eth0 rx 8 tx 8
Cannot set device channel parameters: Invalid argument
> dmesg
qlcnic 0000:05:00.0: eth0: No Multi Tx queue support
qlcnic 0000:05:00.0: eth0: Unable to configure 1 Tx rings
qlcnic 0000:05:00.0: eth0: No Multi Tx queue support
qlcnic 0000:05:00.0: eth0: Unable to configure 8 Tx rings
```

so we will use only 4 CPU per NIC using NUMA0 CPUs only:

``` shell
> rss-ladder eth0
- distribute interrupts of eth0 (-rx-) on socket 0
  - eth0: queue eth0-rx-0 (irq 88) bound to CPU0
  - eth0: queue eth0-rx-1 (irq 89) bound to CPU1
  - eth0: queue eth0-rx-2 (irq 90) bound to CPU2
- distribute interrupts of eth0 (-tx--rx-) on socket 0
> rss-ladder eth1 --offset 16
- distribute interrupts of eth1 (-rx-) on socket 0
  - eth1: queue eth1-rx-0 (irq 93) bound to CPU28
  - eth1: queue eth1-rx-1 (irq 94) bound to CPU29
  - eth1: queue eth1-rx-2 (irq 95) bound to CPU30
- distribute interrupts of eth1 (-tx--rx-) on socket 0
```

rss-ladder isn't perfect here, so fix TX queues affinity manually:

```
echo 3 > /proc/irq/91/smp_affinity_list
echo 31 > /proc/irq/96/smp_affinity_list
```

why 28-29, if NUMA0 is NUMA node0 CPU(s):     0-11,24-35? Hyperthreading - 0-3 and 24-27 are the same 4 cores.

## after tuning:


### /proc/interrupts

```
  CPU0   CPU1   CPU2    CPU3   CPU4   CPU5   CPU6   CPU7   CPU8   CPU9   CPU10   CPU11   CPU12   CPU13   CPU14   CPU15   CPU16   CPU17   CPU18   CPU19   CPU20   CPU21   CPU22   CPU23   CPU24   CPU25   CPU26   CPU27   CPU28   CPU29   CPU30   CPU31   CPU32   CPU33   CPU34   CPU35   CPU36   CPU37   CPU38   CPU39   CPU40   CPU41   CPU42   CPU43   CPU44   CPU45   CPU46   CPU47

  6725      0      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-0
     0   8469      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-1
     0      0   5688       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-rx-2
     0      0      0   10238      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth0-tx-0-rx-3
     0      0      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0    7346       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-0
     0      0      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0    9340       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-1
     0      0      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0    8005       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-rx-2
     0      0      0       0      0      0      0      0      0      0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   16015       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0       0   eth1-tx-0-rx-3
  3206   2731   2120    2544    134     90     26     73     17      9      10      10     734     286      94      59      24       8      57      14      16      12       5      13     138     450     246     121    5524    6620    6039   17682      50      25      12      29     127     318     653     175      35      23      12       3      23      13      13      13   interrupts
```

### Load per cpu:

```
  CPU     Interrupts   NET RX   NET TX   total   dropped   time_squeeze   cpu_collision   received_rps

  CPU0          9950     7198     8684    7931         0              0               0              0
  CPU1         11200     8655    10013    9280         0              0               0              0
  CPU2          7808     5798     6550    6099         0              0               0              0
  CPU3         12782    10389     9512    9019         0              0               0              0
  CPU4           134        2       34       4         0              0               0              0
  CPU5            90        2       11       4         0              0               0              0
  CPU6            26        0        0       0         0              0               0              0
  CPU7            77        0       31       0         0              0               0              0
  CPU8            17        2       18       4         0              0               0              0
  CPU9             9        0        0       0         0              0               0              0
  CPU10           10        0        0       0         0              0               0              0
  CPU11           10        0        0       0         0              0               0              0
  CPU12          758       93        9     190         0              0               0              0
  CPU13          288        1       10       2         0              0               0              0
  CPU14           95        1       29       2         0              0               0              0
  CPU15           59        0       13       0         0              0               0              0
  CPU16           24        0       14       0         0              0               0              0
  CPU17            8        0        0       0         0              0               0              0
  CPU18           57        1       10       2         0              0               0              0
  CPU19           14        0        0       0         0              0               0              0
  CPU20           16        0        0       0         0              0               0              0
  CPU21           12        0        0       0         0              0               0              0
  CPU22            5        0        0       0         0              0               0              0
  CPU23           13        0        0       0         0              0               0              0
  CPU24          141        1       38       2         0              0               0              0
  CPU25          457        0       24       0         0              0               0              0
  CPU26          247        3       71       6         0              0               0              0
  CPU27          121        1       42       2         0              0               0              0
  CPU28        12870     7668    11076    9870         0              0               0              0
  CPU29        15960     9556    13795   12050         0              0               0              0
  CPU30        14044     8219    12337   10531         0              0               0              0
  CPU31        33697    16251    30557   15912         0              0               0              0
  CPU32           50        0        4       0         0              0               0              0
  CPU33           64        0        0       0         0              0               0              0
  CPU34           12        0        0       0         0              0               0              0
  CPU35           29        1        6       2         0              0               0              0
  CPU36          128       91        0     182         0              0               0              0
  CPU37          355        0       26       0         0              0               0              0
  CPU38          662        1        0       4         0              0               0              0
  CPU39          175        0        0       0         0              0               0              0
  CPU40           35        1       20       2         0              0               0              0
  CPU41           24        0        1       0         0              0               0              0
  CPU42           12        0        7       0         0              0               0              0
  CPU43            3        0        0       0         0              0               0              0
  CPU44           23        0        2       0         0              0               0              0
  CPU45           13        0        0       0         0              0               0              0
  CPU46           13        0        0       0         0              0               0              0
  CPU47           13        0        0       0         0              0               0              0
```

### Network devices

```
  Device      rx-packets   rx-mbits   rx-errors   dropped   missed   fifo   length   overrun   crc   frame    tx-packets    tx-mbits   tx-errors

  lo                1947         31           0         0        0      0        0         0     0       0          1947          31           0
  imq0             25792         74           0         0        0      0        0         0     0       0         25804          74           0
  imq1             52601        471           0         0        0      0        0         0     0       0         52728         471           0
  eth0             30637         85           0         0        0      0        0         0     0       0   13929354647   126126622           0
  eth1             55783        500           0         0        0      0        0         0     0       0    8356885217    23795134           0
  eth6                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth7                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth5                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth4                 0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.10            108          0           0         0        0      0        0         0     0       0           108           0           0
  eth0.100          4552          7           0         0        0      0        0         0     0       0          8605          84           0
  eth0.101           339          1           0         0        0      0        0         0     0       0           497           4           0
  eth0.102          9582         29           0         0        0      0        0         0     0       0         16697         152           0
  eth0.1022         2146          8           0         0        0      0        0         0     0       0          3396          29           0
  eth0.103          2990          7           0         0        0      0        0         0     0       0          5378          49           0
  eth0.104          8727         27           0         0        0      0        0         0     0       0         16303         144           0
  eth0.105            64          0           0         0        0      0        0         0     0       0            22           0           0
  eth0.106             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.107             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.108             0          0           0         0        0      0        0         0     0       0             0           0           0
  eth0.109          2047          2           0         0        0      0        0         0     0       0          4238          36           0
  dummy0               0          0           0         0        0      0        0         0     0       0             0           0           0
```

## Finally

Load is distributed, but `time_squeeze`'s still grow sometimes. After this next steps:

- disable hyperthreading
- reboot
- re-setup all this
