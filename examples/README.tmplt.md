# lscpu

``` shell
lscpu
```

``` shell
lscpu -p
```

# ethtool

``` shell

devices=( eth1 eth2 eth3 )
for dev in "${devices[@]}"; do
  echo "## $dev"
  ethtool -i $dev
  ethtool -g $dev
  ethtool -l $dev
done
```

# before and after

## before tuning:

```
network-top --no-clear -n 1
```

## commands

Replace this example with command you've run on your server and delete this line.

``` shell
# eth0 just receiving traffic
rss-ladder eth0
rx-buffers-increase eth0

# eth1 and eth2 have only single queue, but they are doing forwarding
for dev in eth1 eth2; do
  for tune in autorps autoxps; do
    $tune --cpu-mask=fc0 $dev
  done
done
```

## after tuning:

```
network-top --no-clear -n 1
```
