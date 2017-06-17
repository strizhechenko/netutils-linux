#!/usr/bin/env python

"""The setup and build script for the netutils-linux."""

import os
import setuptools


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setuptools.setup(
    name='netutils-linux',
    version='1.3.4',
    author='Oleg Strizhechenko',
    author_email='oleg.strizhechenko@gmail.com',
    license='MIT',
    url='https://github.com/strizhechenko/netutils-linux',
    keywords='linux network performanse utils troubleshooting irq interrupts softirqs proc',
    description='Bunch of utils to simplify linux network troubleshooting and performance tuning.',
    long_description=(read('README.rst')),
    packages=setuptools.find_packages(exclude=['tests*']),
    scripts=[os.path.join('utils/', script) for script in os.listdir('utils/')],
    install_requires=['pyyaml', 'ipaddress', 'six', 'colorama', 'prettytable'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
