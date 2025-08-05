#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python SDK for Dexodus perpetual futures trading platform"

setup(
    name="dexodus-perps-sdk",
    version="1.1.1",
    description="Python SDK for Dexodus perpetual futures trading platform on Base",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Dexodus Team",
    author_email="dev@dexodus.com",
    url="https://github.com/dexodus/perps-sdk-python",
    packages=find_packages(),
    package_data={
        'dexodus_perps_sdk': ['*.js', 'examples/*.py']
    },
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    keywords=["dexodus", "perpetual", "futures", "trading", "defi", "base"],
    license="MIT",
    zip_safe=False,
)
