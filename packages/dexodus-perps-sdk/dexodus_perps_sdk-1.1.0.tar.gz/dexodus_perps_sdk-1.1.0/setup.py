#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Python SDK for Dexodus perpetual futures trading platform (v1.1.0 - Simplified Configuration)"

setup(
    name="dexodus-perps-sdk",
    version="1.1.0",
    description="Python SDK for Dexodus perpetual futures trading platform on Base (v1.1.0 - Simplified Configuration)",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Dexodus Team",
    author_email="dev@dexodus.com",
    url="https://github.com/dexodus/perps-sdk-python",
    project_urls={
        "Documentation": "https://docs.dexodus.com/sdk",
        "Source": "https://github.com/dexodus/perps-sdk-python",
        "Tracker": "https://github.com/dexodus/perps-sdk-python/issues",
        "Discord": "https://discord.gg/dexodus",
        "JavaScript SDK": "https://www.npmjs.com/package/dexodus-perps-sdk"
    },
    packages=find_packages(),
    package_data={
        'dexodus_perps_sdk': [
            '*.js',
            'examples/*.py'
        ]
    },
    include_package_data=True,
    install_requires=[
        # No Python dependencies - uses Node.js internally
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed"
    ],
    keywords=[
        "dexodus", "perpetual", "futures", "trading", "defi", "base", 
        "blockchain", "ethereum", "sdk", "api", "perps", "derivatives",
        "cryptocurrency", "finance", "simplified", "gasless"
    ],
    license="MIT",
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'dexodus-perps-test=dexodus_perps_sdk.examples.test_python_wrapper:main',
        ],
    }
)
