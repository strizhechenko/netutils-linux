FROM centos:6


MAINTAINER Oleg Strizhechenko version: 0.1

RUN yum -y update
RUN yum -y groupinstall development
RUN yum -y install epel-release
RUN yum -y install ruby-devel gcc make rpm-build rubygems python-pip libffi-devel readline-devel sqlite-devel zlib-devel libyaml-devel openssl-devel
ADD fpm.sh /root/fpm.sh
RUN bash -x /root/fpm.sh
ADD netutils.sh /root/netutils.sh

CMD ["/bin/bash"]
