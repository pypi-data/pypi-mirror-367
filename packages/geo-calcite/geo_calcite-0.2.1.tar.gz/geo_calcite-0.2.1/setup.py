# Copyright 2025 Zhejiang University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND.

from setuptools import setup, find_packages

setup(
    name="geo_calcite",
    version="0.2.1",
    description="Python client for Geo-Calcite data service",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Zhejiang University",
    url="https://code.deep-time.org/Aoicat/geo-calcite-python-client",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.0.0",
        "pandas>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="Apache License 2.0"
)
