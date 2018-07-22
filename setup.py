#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from os import path
from codecs import open

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

exec(open('py_trace/_version.py').read())

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs
                    if x.startswith('git+')]

# get the dependencies and installs
with open(path.join(here, 'requirements_dev.txt'), encoding='utf-8') as f:
    dev_requires = f.read().split('\n')

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Diego Fernandez",
    author_email='aiguo.fernandez@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Python client for interacting with the Trace api.",
    install_requires=install_requires,
    dependency_links=dependency_links,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='py_trace',
    name='py_trace',
    packages=find_packages(include=['py_trace']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    extras_require={
        'dev': dev_requires
    },
    url='https://github.com/aiguofer/py-trace',
    version=__version__,
    zip_safe=False,
)
