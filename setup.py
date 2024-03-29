#!/usr/bin/env python
# coding=utf-8

"""The setup and build script for the netutils-linux."""

import os

import setuptools


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setuptools.setup(
    name='netutils-linux',
    version='2.8.0',
    author='Oleg Strizhechenko',
    author_email='oleg.strizhechenko@gmail.com',
    license='MIT',
    url='https://github.com/strizhechenko/netutils-linux',
    keywords='linux network performanse utils troubleshooting irq interrupts softirqs proc',
    description='Bunch of utils to simplify linux network troubleshooting and performance tuning.',
    long_description=(read('README.rst')),
    long_description_content_type='text/x-rst',
    packages=setuptools.find_packages(exclude=['tests*']),
    scripts=[os.path.join('utils/', script) for script in os.listdir('utils/')],
    install_requires=['pyyaml', 'ipaddress', 'six', 'colorama', 'prettytable', 'argparse'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
