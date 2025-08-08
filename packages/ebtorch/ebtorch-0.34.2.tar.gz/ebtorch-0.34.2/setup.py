#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ──────────────────────────────────────────────────────────────────────────────
#
#  Copyright (c) 2020-2025 Emanuele Ballarin <emanuele@ballarin.cc>
#  Released under the terms of the MIT License
#  (see: https://url.ballarin.cc/mitlicense)
#
# ──────────────────────────────────────────────────────────────────────────────
#
# SPDX-License-Identifier: MIT
#
# ──────────────────────────────────────────────────────────────────────────────
import os

from setuptools import find_packages
from setuptools import setup


def read(fname) -> str:
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read().strip()


PACKAGENAME: str = "ebtorch"

setup(
    name=PACKAGENAME,
    version="0.34.2",
    author="Emanuele Ballarin",
    author_email="emanuele@ballarin.cc",
    url="https://github.com/emaballarin/ebtorch",
    description="Collection of PyTorch additions, extensions, utilities, uses and abuses",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords=["Deep Learning", "Machine Learning"],
    license="Apache-2.0",
    packages=[package for package in find_packages() if package.startswith(PACKAGENAME)],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.10",
    install_requires=[
        "advertorch>=0.2.3",  # pip install git+https://github.com/BorealisAI/advertorch.git
        "distributed>=2024.12.1",
        "httpx>=0.27",
        "matplotlib>=3.8",
        "medmnist>=3",
        "numpy>=1.24",
        "pillow>=9.5",
        "PyYAML>=6.0.2",
        "requests>=2.25",
        "safe_assert>=0.5",
        "safetensors>=0.5.3",
        "setuptools>=75.8.2",
        "thrmt>=0.0.6",
        "torch>=2.5",
        "torch-lr-finder>=0.2.1",
        "torchattacks>=3.5.1",
        "torchvision>=0.15",
        "tqdm>=4.65",
    ],
    include_package_data=False,
    zip_safe=True,
)
