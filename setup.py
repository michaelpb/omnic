#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

if sys.argv[-1] == 'test':
    os.system('py.test')
    sys.exit()

readme = open('README.md').read()
doclink = """
Documentation
-------------

The full documentation is at http://omnic.rtfd.org."""
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='omnic',
    version='0.1.0',
    description='Mostly stateless microservice framework for generating '
    'on-the-fly thumbs and previews of a wide variety of file types.',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='michaelb',
    author_email='michaelpb@gmail.com',
    url='https://github.com/michaelpb/omnic',
    packages=[
        'omnic',
    ],
    package_dir={'omnic': 'omnic'},
    include_package_data=True,
    scripts=['bin/omnic'],
    install_requires=[
    ],
    license='GPL3',
    zip_safe=False,
    keywords='omnic',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
    ],
)
