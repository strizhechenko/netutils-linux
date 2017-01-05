irq-utils
=========

It's just a bunch of utils to simplify linux network troubleshooting and performance tuning.

irqtop
------

- Show you a rate of interrupts
- based on /proc/interrupts file
- Hides interrupts with small rate to show a better picture.

softirq-net-rx-top
------

- Show you a rate of receiving packets
- Based on /proc/softirq
- Sometimes shows much more CPUs than really exists

missed-pkts-monitor
------

- Detects when were packets missed (maybe it will give some idea of correlation with something)
- Easy to use in tactical, not strategic debug, without deployment of graphite/influxdb

link-rx-rate
------

- Shows how many packets/bytes network interface receives

rss-ladder
------

Automatically set smp_affinity_list for IRQ of NIC rx/tx queues for ixgbe/igb/vmxnet3 drivers (they usually work on CPU0 out of box).

Later, it will get support for double ladder in case of multiprocessor systems.

autorps
------

Enables RPS of NIC on all available CPUs. It may be good for small servers with cheap network cards or bunch of VLAN.

Later, it will get support for enable RPS only for subgroup of CPUs based on L3 caches.
