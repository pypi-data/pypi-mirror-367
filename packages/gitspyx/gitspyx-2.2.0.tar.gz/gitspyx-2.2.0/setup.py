#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gitspyx",
    version="2.2.0",
    author="Alex Butler [Vritra Security Organization]",
    description="Advanced GitHub Intelligence Tool - OSINT tool for GitHub reconnaissance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VritraSecz/GitSpyX",
    project_urls={
        "Bug Reports": "https://github.com/VritraSecz/GitSpyX/issues",
        "Source": "https://github.com/VritraSecz/GitSpyX",
        "Documentation": "https://github.com/VritraSecz/GitSpyX#readme",
    },
    packages=find_packages(),
    py_modules=["gitspyx"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gitspyx=gitspyx:main",
        ],
    },
    keywords="osint github intelligence reconnaissance security tool cybersecurity",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
