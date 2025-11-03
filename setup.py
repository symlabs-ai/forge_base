"""
Setup configuration for ForgeBase.

Author: Jorge, The Forge
Created: 2025-11-03
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION.MD", "r", encoding="utf-8") as fh:
    version = fh.read().strip().split()[-1]

setup(
    name="forgebase",
    version=version,
    author="Jorge, The Forge",
    author_email="forge@forgebase.dev",
    description="Cognitive Architecture Framework - Clean + Hexagonal Architecture with native observability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/forgeframework/forgebase",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        # Core dependencies will be added as needed
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pydocstyle>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
)
