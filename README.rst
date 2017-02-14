netutils-linux
======

.. image:: https://travis-ci.org/strizhechenko/netutils-linux.svg?branch=master
   :target: https://travis-ci.org/strizhechenko/netutils-linux

It's just a bunch of utils to simplify Linux network troubleshooting and performance tuning.

Project state
======
Beta. Few script were gathered together, shortly documented, one has some tests and packed into python package.

Some were cleaned up, some - not. Most of them were being written in bash, not python, maybe they'll be ported later.

In next few weeks, it will receive something like a 'tuned' with autodetection of best settings for all the system feature.

Installation
======
.. code :: shell

  pip install netutils-linux

Utils
======

irqtop
------
- Show you a rate of interrupts
- based on /proc/interrupts file
- Hides the interrupts with small rate to show a better picture.

softirq-net-rx-top
------
- Show you a rate of receiving packets
- Based on /proc/softirqs
- Sometimes shows much more CPUs than really exists

missed-pkts-monitor
------
- Detects when were packets missed (maybe it will give some idea of correlation with something)
- Easy to use in tactical, not strategic debug, without deployment of graphite/influxdb
- Based on `ip -s -s link` output

link-rx-rate
------
- Shows how many packets/bytes network interface receives
- Based on /proc/net/dev

rss-ladder
------
Automatically set `smp_affinity_list` for IRQ of NIC rx/tx queues for ixgbe/igb/vmxnet3 drivers (they usually work on CPU0 out of the box).

Based on lscpu's output.

It also supports double/quad ladder in case of multiprocessor systems (but you better explicitly specify queue count == core per socket as NIC's driver's param).

autorps
------
Enables RPS of NIC on all available CPUs. It may be good for small servers with cheap network cards or a bunch of VLAN.

Later, there will be a support for enabling RPS only for a subgroup of CPUs based on L3 caches.

maximize-cpu-freq
------
Sets every CPU scaling governor mode to performance and set max scaling value for min scaling value. So you will be able to use all power of your processor (useful for latency sensible systems).

rx-buffers-increase
------
rx-buffers-increase is util, that finds and sets compromise value between avoiding dropped/missing pkts and keeping a latency low.
