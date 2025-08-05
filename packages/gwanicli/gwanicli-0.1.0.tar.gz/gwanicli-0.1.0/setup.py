"""
GwaniCLI - A command-line interface for accessing Quranic verses and translations.

A simple and elegant CLI tool for reading Quranic verses with multiple translation
options, caching for offline access, and beautiful console formatting.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(
    encoding='utf-8') if (this_directory / "README.md").exists() else __doc__

# Read requirements
requirements_path = this_directory / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip()
                        and not line.startswith('#')]

setup(
    name="gwanicli",
    version="0.1.0",
    author="Hamza Danjaji",
    author_email="bhantsi@gmail.com",
    description="A command-line interface for accessing Quranic verses and translations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bhantsi/gwani-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Religion",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.11",
    install_requires=requirements or [
        "click>=8.0.0",
        "requests>=2.25.0",
        "toml>=0.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "gwani=qwanicli.cli:gwani",
        ],
    },
    keywords="quran, islam, cli, terminal, verses, translation",
    project_urls={
        "Bug Reports": "https://github.com/bhantsi/gwani-cli/issues",
        "Source": "https://github.com/bhantsi/gwani-cli",
        "Documentation": "https://github.com/bhantsi/gwani-cli#readme",
    },
)
