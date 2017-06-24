#!/bin/bash

if python --version 2>&1 | grep -qi 'Python 2.6'; then
	echo "WARNING: flake8 doesn't support 2.6, skip linting (it'll be done in 2.7/3.4/3.6 checks)"
	exit 0
fi

flake8 "$@"
