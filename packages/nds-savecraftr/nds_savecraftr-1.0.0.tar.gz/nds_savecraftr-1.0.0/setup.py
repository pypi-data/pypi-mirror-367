#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="nds-savecraftr",
    version="1.0.0",
    author="tcsenpai",
    author_email="tcsenpai@discus.sh",
    description="Universal Nintendo DS Save File Craftr",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tcsenpai/nds-savecraftr",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Topic :: Utilities",
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
    install_requires=[
        # No external dependencies needed!
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "nds-savecraftr=nds_savecraftr.cli:main",
            "savecraftr=nds_savecraftr.cli:main",
        ],
    },
    keywords="nintendo ds save converter twilight menu r4 flashcart emulator craftr",
    project_urls={
        "Bug Reports": "https://github.com/tcsenpai/nds-savecraftr/issues",
        "Source": "https://github.com/tcsenpai/nds-savecraftr",
        "Documentation": "https://github.com/tcsenpai/nds-savecraftr/blob/main/README.md",
    },
)