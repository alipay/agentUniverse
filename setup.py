# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/8 16:17
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: setup.py

import setuptools

with open("README_PYPI.md", "r") as fh:
    long_description = fh.read()


def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')

    return requirements


setuptools.setup(
    name="agentUniverse",
    version="0.0.5",
    author="AntGroup",
    author_email="jerry.zzw@antgroup.com",
    description="agentUniverse is a framework for developing applications powered "
                "by multi-agent base on large language model.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/agentUniverse/agentUniverse",
    packages=setuptools.find_packages(exclude=["*sample_standard_app*", "*docs*", "*tests*"]),
    package_data={
            '': ['*.yaml'],
        },
    install_requires=read_requirements(),
    classifiers=[
        'Programming Language :: Python :: 3.10',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
