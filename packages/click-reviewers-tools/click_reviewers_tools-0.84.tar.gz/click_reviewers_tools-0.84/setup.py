#! /usr/bin/env python3

from setuptools import setup, find_packages
import codecs
import glob
import os
import re

# look/set what version we have
changelog = 'debian/changelog'
if os.path.exists(changelog):
    head = codecs.open(changelog, encoding='utf-8').readline()
    match = re.compile('.*\(([.\d]+).*\).*').match(head)
    if match:
        version = match.group(1)

scripts = glob.glob('bin/click-*')
scripts.remove('bin/click-check-skeleton')

requirements = [
    'python-magic',
    'PyYaml',
    'lxml',
    'pyxdg',
    'python-apt',
    'python-debian',
]

setup(
    name='click-reviewers-tools',
    version=version,
    scripts=scripts,
    packages=find_packages(),
    test_suite='clickreviews.tests',
    install_requires=requirements,
)
