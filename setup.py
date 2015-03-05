#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='PyAfip',
    version='1.0.0',
    author='Hugo Osvaldo Barrera',
    author_email='hugo@barrera.io',
    packages=['afip', 'afip.wsfev1'],
    url='https://github.com/hobarrera/PyAFIP.git',
    license='LICENSE',
    description="A basic python library for accesing some of AFIP's web" +
        "services.",
    # long_description=open('README.md').read(),
    requires=[
        "suds (>= 0.4)",
        "M2Crypto (>= 0.22.3)",
        "lxml (>=3.3.4)"
    ]
)
