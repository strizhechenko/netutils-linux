Most utils are designed to be tested without need to have a real hardware (there should be a lot different machines for every developer). Almost every utility allows to specify "test" data source such as lscpu's output, /proc/interrupts or /proc/net/softnet_stat files' snapshot etc.

This directory contains few snapshots for autotests. Unfortunatedly they aren't standardized yet. I have idea to structurize this directory the same way as examples directory: 

```
./tests/sockets_${socket_count}_cpus_${cpu_per_socket}_nic_${netdevs_count}(_duplicate_index)?
```

and every directory should have data for every utility.
