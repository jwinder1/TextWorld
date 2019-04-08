#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.


import os

from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.build_py import build_py


def _pre_install(dir):
    from subprocess import check_call
    check_call(['./setup.sh'], shell=True, cwd=os.getcwd())


class CustomInstall(install):
    def run(self):
        self.execute(_pre_install, (self.install_lib,),
                     msg="Running post install task")
        install.run(self)


class CustomDevelop(develop):
    def run(self):
        self.execute(_pre_install, (self.install_lib,),
                     msg="Running post install task")
        develop.run(self)


class CustomBuildPy(build_py):
    def run(self):
        _pre_install(None)
        build_py.run(self)


required_pkgs = [
    "numpy>=1.13.1",
    "tqdm>=4.17.1",
    "cffi>=1.0.0",
    "networkx>=2",
    "pyyaml>=3.12",
    "urwid>=2.0.1",
    "more_itertools",
    "tatsu>=4.3.0",
    "hashids>=1.2.0",
    "jericho>=1.1.5",
    "pybars3>=0.9.3",
    "flask>=1.0.2",
    "selenium>=3.12.0",
    "greenlet==0.4.13",
    "gevent==1.3.5",
    "pillow>=5.1.0",
    "pydot>=1.2.4",
    "prompt_toolkit<2.1.0,>=2.0.0",
    "gym>=0.10.11"
]


setup(
    name='textworld',
    version=open(os.path.join("textworld", "version.py")).read().split("=")[-1].strip("' \n"),
    author='',
    cmdclass={
        'build_py': CustomBuildPy,
        'install': CustomInstall,
        'develop': CustomDevelop
    },
    packages=find_packages(),
    include_package_data=True,
    scripts=[
        "scripts/tw-data",
        "scripts/tw-play",
        "scripts/tw-make",
        "scripts/tw-stats",
        "scripts/tw-extract",
    ],
    license='',
    zip_safe=False,
    description="Microsoft Textworld - A Text-based Learning Environment.",
    cffi_modules=["glk_build.py:ffibuilder"],
    setup_requires=['cffi>=1.0.0'],
    install_requires=required_pkgs,
    test_suite='nose.collector',
    tests_require=[
        'nose==1.3.7',
    ],
)
