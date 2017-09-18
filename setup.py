# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

INSTALL_REQUIREMENTS = [
    'Click>=6.0,<7.0',
    'click_log>=0.2.0,<0.3.0',
    'requests>=2.9.1',
    'APScheduler>=3.3.1,<4.0',
]

setup(
    author='Jonas Ohrstrom',
    author_email='ohrstrom@gmail.com',
    url='https://github.com/ohrstrom/obp-pad-composer',
    name='obp-pad-composer',
    version='0.0.1',
    description='DAB+ Pad data composer (for Open Broadcast API)',
    packages=find_packages(),
    install_requires=INSTALL_REQUIREMENTS,
    entry_points='''
        [console_scripts]
        pad-composer=pad_composer:cli
    ''',
)
