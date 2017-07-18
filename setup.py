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

readme = open('README.rst').read()

setup(
    name='omnic',
    version='0.1.1',
    description='Mostly stateless microservice framework for generating '
    'on-the-fly thumbs and previews of a wide variety of file types.',
    long_description=readme,
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
        'python-magic',
        'aiohttp',
        'async_timeout',
    ],
    license='GPL3',
    zip_safe=False,
    keywords='omnic',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Framework :: AsyncIO',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
    ],
)
