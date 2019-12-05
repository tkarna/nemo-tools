#!/usr/bin/env python

from distutils.core import setup

setup(
    name='NemoTools',
    version='0.1',
    description='Utils for Nemo ocean model',
    author='Tuomas Karna',
    author_email='tuomas.karna@gmail.com',
    url='https://github.com/tkarna/nemo-tools',
    packages=setuptools.find_packages(),
    scripts=[
        'scripts/compare-namelist',
        'scripts/nemo-progress',
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
