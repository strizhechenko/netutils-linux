FROM centos:latest


MAINTAINER Oleg Strizhechenko version: 0.1

RUN yum -y install epel-release && yum -y update
RUN yum -y install ruby-devel gcc make rpm-build rubygems python-pip
RUN gem install --no-ri --no-rdoc fpm
ADD netutils.sh /root/netutils.sh
RUN pip install setuptools

CMD ["/bin/bash"]
