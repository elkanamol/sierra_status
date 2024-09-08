"""
Defines the setup configuration for the sierra_flasher package.

This setup configuration includes the package metadata, such as the name, version, description, author, license, and URLs for the project. It also specifies the required Python version, the packages to be included, and the console script entry point.
"""

from sierra_status.__version__ import __version__
from setuptools import setup, find_packages
import os

version = __version__
# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""
requirement_path = f"{current_directory}/requirements.txt"
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()


"""
Defines the setup configuration for the sierra-status package.

This setup configuration includes the package metadata, such as the name, version, description, author, license, and URLs for the project. It also specifies the required Python version, the packages to be included, and the console script entry point.
"""
setup(
    name="sierra_status",
    version=version,
    packages=find_packages(),
    description="CLI tool for Sierra Wireless EM9xxx/EM7xxx modules to query status",
    author="Elkana Molson",
    author_email="elkanamol@gmail.com",
    long_description=long_description,
    license="MIT",
    url="https://github.com/elkanamol/sierra_status",
    project_urls={
        "Documentation": "https://github.com/elkanamol/sierra_status/blob/main/README.md",
        "Source": "https://github.com/elkanamol/sierra_status",
        "Tracker": "https://github.com/elkanamol/sierra_status/issues",
    },
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "sierra-status = sierra_status.src.cli:main",
        ],
    },
    python_requires=">=3.8",  # Requires Python 3.8 and above
)
