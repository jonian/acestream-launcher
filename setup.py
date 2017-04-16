# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='acestream-launcher',
    version='0.5.0',
    author='Jonian Guveli',
    author_email='jonian@hardpixel.eu',
    scripts=['acestream_launcher.py'],
    url='https://github.com/jonian/acestream-launcher',
    license='LICENSE',
    description='Acestream Launcher allows you to open Acestream links with a Media Player of your choice.',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'acestream-launcher = acestream_launcher:main'
        ]
    }
)
