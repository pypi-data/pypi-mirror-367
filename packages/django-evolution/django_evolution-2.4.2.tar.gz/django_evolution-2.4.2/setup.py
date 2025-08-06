#!/usr/bin/env python
#
# Setup script for Django Evolution

from setuptools import setup, find_packages
from setuptools.command.test import test

from django_evolution import get_package_version, VERSION


PACKAGE_NAME = 'django_evolution'

download_url = (
    'https://downloads.reviewboard.org/releases/django-evolution/%s.%s/' %
    (VERSION[0], VERSION[1]))


with open('README.rst', 'r') as fp:
    long_description = fp.read()


# Build the package
setup(
    name=PACKAGE_NAME,
    version=get_package_version(),
    license='BSD',
    description=('A database schema evolution tool for the Django web '
                 'framework.'),
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/beanbaginc/django-evolution',
    author='Beanbag, Inc.',
    author_email='reviewboard@googlegroups.com',
    maintainer='Beanbag, Inc.',
    maintainer_email='reviewboard@googlegroups.com',
    download_url=download_url,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'Django>=1.6,<4.2.999',
        'python2-secrets; python_version == "3.5"',
    ],
    python_requires=','.join([
        '>=2.7',
        '!=3.0.*',
        '!=3.1.*',
        '!=3.2.*',
        '!=3.3.*',
        '!=3.4.*',
        '!=3.5.*',
    ]),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 1',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
