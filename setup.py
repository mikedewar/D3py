#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='d3py',
    version='0.2.3',
    description='d3py',
    author='Mike Dewar, Micha Gorelick and Adam Laiacano',
    author_email='md@bit.ly',
    url='https://github.com/mikedewar/D3py',
    packages=['d3py', 'd3py.geoms', ],
    package_data={'d3py': ['d3.js', 'd3py_template.html']},
    install_requires=[
        'ipython',
        'networkx',
        'numpy',
        'pandas',
    ]
)
