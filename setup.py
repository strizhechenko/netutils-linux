#!/usr/bin/env python

'''The setup and build script for the twitterbot-farm library.'''

import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='netutils-linux',
    version='0.5.0',
    author='Oleg Strizhechenko',
    author_email='oleg.strizhechenko@gmail.com',
    license='MIT',
    url='https://github.com/strizhechenko/netutils-linux',
    keywords='linux network performanse utils troubleshooting irq interrupts softirqs proc',
    description='Bunch of utils to simplify linux network troubleshooting and performance tuning.',
    long_description=(read('README.rst')),
    packages=find_packages(exclude=['tests*']),
    scripts = [os.path.join('utils/', script) for script in os.listdir('utils/')],
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
