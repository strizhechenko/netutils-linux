# Intro

This doc is about how these utils intended to be used.

1. Connect to the server that seems to be overwhelmed with network traffic.
2. Run `server-info --rate --subsystem` to see if the server can process given traffic.
	1. If not - you'll see what is the biggest problem.
	2. You can see details on device level: `server-info --rate --devices`
	3. Or specify a subsystem: `server-info --rate --net`
	4. Or view details instead of rating `server-info --show --memory`
	5. If you see some device has low-performance - replacing it may be the quickest solution.
3. If hardware is ok let's see what happening with current workload with command: `network-top`
	1. It highlights errors and problems with red or yellow color.
	2. It provide you information how load is distributed across the CPUs and network cards.
	3. It shows how devices attached to each other (highlights NUMA-bindings of CPUS and network cards). It can give an idea how to connect them for better cache-hits.
4. If load is not distributed well or there still exist performance problems - you can tune it.
	0. Disable floating CPU-frequency, use `maximize-cpu-freq` command.
	1. Distribute interrupts of multi-queue network cards with `rss-ladder <device>` command.
	2. Apply `autorps <device>` for single-queue network cards.
	3. If everything is distributed well but there is still packet loss - increase buffers with `rx-buffers-incrase <device>`
5. After each applied setting re-check state of network stack with `network-top`
6. Add all commands you used to tune to an autostart script `/etc/rc.local` for example, otherwise it will work until reboot.
	
