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

## Local development

### Server-info

You can pull collected archive such a /root/server.tar.gz to your local PC, untar it, for example:

```
. env3/bin/activate
mkdir tests/server-info-show.tests/vscale-vm
cd tests/server-info-show.tests/vscale-vm
scp root@test-server:server.tar.gz ./
tar xfz server.tar.gz
mv server/* ./
rm -rf server server.tar.gz
server-info-show
server-info-rate
```
