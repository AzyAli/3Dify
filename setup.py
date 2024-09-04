import os
from setuptools import setup, find_packages

with open ('requirments.txt') as f:
    requirments = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="3Dify",
    version="0.1.0",
    author="Az Ali",
    author_email="a.y.ali@student.utwente.nl",
    description="A Python package for creating 3d models from geospatial data for flood risk analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AzyAli/3Dify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=requirments,
    entry_points={
        "console_script": [
            "3dify=3dify.cli:main",
        ],
    },
    include_package_data=True,

)