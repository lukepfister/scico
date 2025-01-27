#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SCICO package configuration."""

import os
import os.path
from ast import parse
from builtins import filter, next

from setuptools import find_packages, setup

name = "scico"

# Get version number from scico/__init__.py
# See http://stackoverflow.com/questions/2058802
with open(os.path.join(name, "__init__.py")) as f:
    version = parse(next(filter(lambda line: line.startswith("__version__"), f))).body[0].value.s

packages = find_packages()


longdesc = """SCICO is a Python package for solving imaging inverse problems, with an emphasis on problems arising in scientific imaging applications. One of the primary focuses of the package is providing methods for solving ill-posed inverse problems with the use of an appropriate prior model of the reconstruction space.
"""

install_requires = ["numpy", "scipy", "imageio", "jax"]
tests_require = ["pytest", "pytest-runner"]
python_requires = ">3.8"


setup(
    name=name,
    version=version,
    description="Scientific Computational Imaging COde: A Python "
    "package for scientific imaging problems",
    long_description=longdesc,
    keywords=["Computational Imaging", "Inverse Problems", "Optimization", "ADMM", "PGM"],
    platforms="Any",
    license="BSD",
    url="https://github.com/bwohlberg/scico",
    author="SCICO Developers",
    author_email="brendt@ieee.org",  # Temporary
    packages=packages,
    package_data={"scico": ["data/*/*.png", "data/*/*.npz"]},
    include_package_data=True,
    python_requires=python_requires,
    tests_require=tests_require,
    install_requires=install_requires,
    extras_require={
        "tests": tests_require,
        "docs": ["sphinx >=3.5.2", "numpydoc", "sphinxcontrib-bibtex"],
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
