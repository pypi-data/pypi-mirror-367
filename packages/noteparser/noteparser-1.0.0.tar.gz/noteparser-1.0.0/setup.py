"""Setup script for noteparser package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [req for req in requirements if req and not req.startswith("#")]

# Development requirements
dev_requirements = (this_directory / "requirements-dev.txt").read_text().splitlines()
dev_requirements = [req for req in dev_requirements if req and not req.startswith("#") and not req.startswith("-r")]

setup(
    name="noteparser",
    version="1.0.0",
    description="A comprehensive document parser for converting academic materials to Markdown and LaTeX",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/noteparser",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "all": requirements + dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "noteparser=noteparser.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    keywords="markdown latex document parser academic notes converter pdf ocr",
)