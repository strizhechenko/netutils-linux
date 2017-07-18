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

before tuning:

```
network-top --no-clear -n 1
```

after tuning:

```
network-top --no-clear -n 1
```
