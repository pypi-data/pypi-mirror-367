# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloOps",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description=(
        "Unified, production-ready file and directory management for modern Python applications. "
        "Automatically detects project location, manages local/cloud storage, and provides a robust API "
        "for all directory and file operations."
    ),
)
