#!/usr/bin/env bash

IFS=: read _ _ distro _ release _ < /etc/system-release-cpe
if [ "$distro" != "centos" ]; then
	echo "Script written to run in CentOS, not $distro"
fi

fpm -s python -t rpm -d PyYAML --python-disable-dependency pyyaml --rpm-dist "el$release" netutils-linux
