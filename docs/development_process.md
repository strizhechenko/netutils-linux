# Instruments

- PyCharm
- MacOS
- VPS with CentOS 7

## Deployment

Just deploy entire copy of netutils_linux to /root/netutils_linux on CentOS.

Prepare your CentOS:

```
yum -y install python-pip
```

Now you can run:

```
cd /root/netutils_linux
python setup.py install
```

And check if your code really works.
