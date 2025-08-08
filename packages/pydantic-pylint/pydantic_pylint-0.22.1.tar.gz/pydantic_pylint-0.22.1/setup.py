#!/usr/bin/env python3
from setuptools import setup

setup(
    name="pydantic-pylint",
    version="0.22.1",
    py_modules=["sitecustomize"],  # NOT packages!
    author="John W",
    description="A Pylint plugin to help Pylint understand Pydantic",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
