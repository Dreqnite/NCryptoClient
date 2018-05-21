# -*- coding: utf-8 -*-
"""
Module for NCryptoСдшуте package distribution.
"""
from setuptools import setup, find_packages

setup(
    name='NCryptoClient',
    version='0.5.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyQt5>=5.10.1',
        'NCryptoTools>=0.5.2'
    ],
    description='A client-side application of the NCryptoChat',
    author='Andrew Krylov',
    author_email='AndrewKrylovNegovsky@gmail.com',
    license='GNU General Public License v3.0',
    keywords=['Client', 'PyQt5', 'Threads'],
    entry_points={
        'console_scripts': ['NCryptoClient_console = NCryptoClient.launcher:main'],
        'gui_scripts': ['NCryptoClient_gui = NCryptoClient.launcher:main']
    }
)
