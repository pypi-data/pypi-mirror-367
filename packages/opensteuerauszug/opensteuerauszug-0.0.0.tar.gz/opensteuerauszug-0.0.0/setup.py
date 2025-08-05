
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# invalid email
# download url
# url
# project urls

setup(
    name ="opensteuerauszug",
    packages=[".",],
    version='0.0.0',
    description="Generate Swiss tax statements from financial data (placeholder).",
    long_description="""
## Overview
opensteuerauszug is a Python library for doing awesome things.
This name has been reserved using [Reserver](https://github.com/openscilab/reserver).
""",
    long_description_content_type='text/markdown',
    author="Open Steuerauszug Team",
    author_email="38109466+vroonhof@users.noreply.github.com",
    url="https://github.com/vroonhof/opensteuerauszug",
    download_url="https://github.com/vroonhof/opensteuerauszug/archive/refs/heads/main.zip",
    keywords="python3 python reserve reserver reserved",
    project_urls={
            'Source':"https://github.com/vroonhof/opensteuerauszug",
    },
    install_requires="",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    license="MIT",
)

