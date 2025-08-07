#!/usr/bin/env python
"""Setup script for autodoc-typer."""

from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    package_data={
        'autodoc': ['templates/*.j2'],
    },
    entry_points={
        'console_scripts': [
            'autodoc=autodoc.cli:app',
        ],
    },
)