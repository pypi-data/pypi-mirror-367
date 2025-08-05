from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pydwg",
    version="1.0.0",
    author="Sanjeev Bashyal",
    author_email="sanjeev.bashyal01@gmail.com",
    description="A Python package for generating drilling patterns for tunnel excavation based on AutoCAD polylines",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/SanjeevBashyal/UTHP",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "pydwg=pydwg.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pydwg": ["*.txt", "*.md"],
    },
    keywords="drilling pattern tunnel excavation autocad civil engineering mining",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pydwg/issues",
        "Source": "https://github.com/yourusername/pydwg",
        "Documentation": "https://github.com/yourusername/pydwg#readme",
    },
) 