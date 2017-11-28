#!/usr/bin/env bash

. /etc/os-release

fpm -s python -t rpm -d PyYAML --python-disable-dependency pyyaml --python-disable-dependency argparse --rpm-dist "${ID/fedora/fc}${VERSION_ID}" netutils-linux
