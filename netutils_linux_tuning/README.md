# What is this?

Utilities designed to simplify tuning of linux network stack and keep you from manually evaluate affinity maps / cpu masks.

# How it's designed?

- BaseTune
  - RxBuffers - increases RX-buffers of NIC (ethtool -G eth1 rx 2048)
  - CPUBasedTune
    - RSSLadder - sets CPU affinity for NIC's queues
    - AutoSoftirqTune
      - AutoRPSTune - sets RPS cpu mask
      - AutoXPSTune - sets XPS cpu mask
