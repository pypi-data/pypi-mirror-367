#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mkdocs-video2-plugin",
    version="0.0.1",
    description="Embedding of videos in generated mkdocs files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="mkdocs plugin",
    url="https://github.com/mihaigalos/mkdocs-video2-plugin",
    author="Mihai Galos",
    author_email="mihai@galos.one",
    license="MIT",
    python_requires=">=3.8",
    install_requires=["mkdocs>=1.0.4", "mkdocs-material"],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
            "black",
        ],
    },
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(),
    entry_points={
        "mkdocs.plugins": [
            "mkdocs-video2-plugin = mkdocs_video2_plugin.plugin:Video2"
        ]
    },
)
