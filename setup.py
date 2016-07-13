# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'boto',
    'retrying'
]

setup(
    name="ha-release",
    version="0.1.0",
    description="Phase in new EC2 Instances into an AWS Autoscaling Group without Downtime",
    license="MIT",
    author="adamar",
    packages=find_packages(),
    install_requires=install_requires,
    scripts=['ha-release'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
