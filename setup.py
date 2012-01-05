"""
Read It!
========

"""

from __future__ import print_function
import os.path, re
from setuptools import setup

installation_requirements = []
testing_requirements = []

if os.path.exists('requirements.txt'):
    patn = re.compile('[<=>]')
    requirements = open('requirements.txt', 'rb')
    for line in requirements:
        installation_requirements.append(patn.split(line)[0])
    requirements.close()
else:
    print('Warning: cannot find requirements.txt, is your package complete?')

setup(
    name = 'Read It',
    version = '1.0',
    url = 'http://github.com/daveshawley/readit',
    license = 'BSD',
    author = 'Dave Shawley',
    author_email = 'daveshawley@gmail.com',
    description = 'Read article tracker',
    long_description = __doc__,
    packages = ['readit'],
    namespace_packages = ['readit'],
    zip_safe = False,
    platforms = 'any',
    install_requires = installation_requirements,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    )

