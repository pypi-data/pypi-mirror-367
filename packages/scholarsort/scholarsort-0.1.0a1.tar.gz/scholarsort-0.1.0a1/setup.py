"""
Setup script for ScholarSort
"""

from setuptools import setup, find_packages

# Read the requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="scholarsort",
    version="0.1.0a1",
    description="A Python library for scholarly research with impact factor analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ScholarSort Team",
    author_email="team@scholarsort.org",
    url="https://github.com/scholarsort-team/scholarsort",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.8",
    keywords="scholarly research impact factor academic citations",
    project_urls={
        "Documentation": "https://scholarsort.readthedocs.io/",
        "Source": "https://github.com/scholarsort-team/scholarsort",
        "Tracker": "https://github.com/scholarsort-team/scholarsort/issues",
    },
)
