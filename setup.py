# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'boto',
    'retrying'
]

setup(
    name="ha-release",
    version="0.1.0",
    description="Phase new EC2 Instances into an AWS Autoscaling Group without Downtime",
    license="MIT",
    author="adamar",
    author_email="none@none.com",
    url="http://github.com/adamar/ha-release",
    packages=find_packages(),
    install_requires=install_requires,
    scripts=['ha-release.py'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
