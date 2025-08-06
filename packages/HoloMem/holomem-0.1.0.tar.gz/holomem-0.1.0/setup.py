# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="HoloMem",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Pillow",
        "rapidfuzz",
        "numpy",
        "SynMem"
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="A Modern 4-Stage Synthetic Memory",
)
