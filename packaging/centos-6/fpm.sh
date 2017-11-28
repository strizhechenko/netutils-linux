#!/usr/bin/env bash

curl -sSL https://rvm.io/mpapis.asc | gpg2 --import -
curl -L get.rvm.io | bash -s stable
source /etc/profile.d/rvm.sh && rvm reload && rvm install 2.1.0
gem install --no-ri --no-rdoc fpm
