#!/bin/bash

set -eux

link-rate --random  --devices=eth1,eth2,eth3 --iterations=1 | grep -q 'rx-mbits'
link-rate --bits --random  --devices=eth1,eth2,eth3 --iterations=1 | grep -q 'rx-bits'
link-rate --kbits --random  --devices=eth1,eth2,eth3 --iterations=1 | grep -q 'rx-kbits'
link-rate --mbits --random  --devices=eth1,eth2,eth3 --iterations=1 | grep -q 'rx-mbits'
link-rate --bytes --random  --devices=eth1,eth2,eth3 --iterations=1 | grep -q 'rx-bytes'
