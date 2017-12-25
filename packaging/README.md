# Packaging

## Fedora/RHEL/CentOS

```
➜  centos-6 git:(master) ✗ docker build .
Sending build context to Docker daemon  3.072kB
Step 1/6 : FROM fedora:latest
 ---> a602963ff8cd
Step 2/6 : MAINTAINER Oleg Strizhechenko version: 0.1
 ---> Using cache
 ---> b4fc07df30ac
Step 3/6 : RUN yum -y update && yum -y install ruby-devel gcc make rpm-build rubygems python-pip
 ---> Using cache
 ---> 55ff073b227d
Step 4/6 : RUN gem install --no-ri --no-rdoc fpm
 ---> Using cache
 ---> e489129118be
Step 5/6 : ADD netutils.sh /root/netutils.sh
 ---> e68b353383e2
Step 6/6 : CMD /bin/bash
 ---> Running in 4a946ca858fc
 ---> eac7b7c73e4c
Removing intermediate container 4a946ca858fc
Successfully built eac7b7c73e4c
➜  centos-6 git:(master) ✗ docker create -t -i eac7b7c73e4c bash
3ca13114d34cea6fddca7e832d7f0be04982c55729db000c2dc56978401eaacb
➜  centos-6 git:(master) ✗ docker start -a -i cf69d0f1cd26b6a21371427eb1e5cda19bd9f18619f0129b32bc326a63bc42cc
[root@cf69d0f1cd26 /]# cd /root/
[root@cf69d0f1cd26 /]# ./netutils.sh
```
