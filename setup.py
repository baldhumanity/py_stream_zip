import os
from setuptools import setup, find_packages

# Read the contents of the README file for the long description.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="py-stream-zip",
    version="0.1.0",
    description="A stream-based ZIP file extractor in Python, inspired by node-stream-zip.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Homepage": "https://github.com/yourusername/py-stream-zip",
        "Repository": "https://github.com/yourusername/py-stream-zip",
        "Credits": "Inspired by node-stream-zip",
    },
    python_requires=">=3.6",
)
