from setuptools import setup, find_packages

# Type hint for List is missing, import it
from typing import List

# Constants
HYPEN_E_DOT = "-e ."

__version__ = "0.0.0"

REPO_NAME = "CineNotes"
AUTHOR_USER_NAME = "paritosh0707 || prakhara56"
SRC_REPO = "cine_notes"
AUTHOR_EMAIL = "paritoshsharma0707@gmail.com || prakhara56@gmail.com"



def get_requirements(file_path: str) -> List[str]:
    """
    Read and parse requirements from a requirements.txt file.
    
    Args:
        file_path (str): Path to the requirements.txt file
        
    Returns:
        List[str]: List of package requirements with newlines removed and -e . filtered out
    """
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

    return requirements

def get_long_description(file_path: str) -> str:
    """
    Read the long description from a file (typically README.md).
    
    Args:
        file_path (str): Path to the description file
        
    Returns:
        str: Content of the file or a default description if file cannot be read
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            long_description = f.read()
    except Exception as e:
        long_description = "Cine Notes is a package to extact Notes from a Video"
    return long_description


setup(
    name=SRC_REPO,
    version=__version__,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=get_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'cine_notes=cine_notes.cli:main',
        ],
    },
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description=get_long_description('README.md'),
    url='https://github.com/paritosh0707/CineNotes',
    project_urls={
        "Bug Tracker": f"https://github.com//{REPO_NAME}/issues",
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
"""
CineNotes Package Setup

This script configures the CineNotes package for distribution using setuptools.
It handles package metadata, dependencies, and entry points.

The setup function configures:
- Package name and version
- Package discovery using find_packages()
- Dependencies from requirements.txt
- Console script entry point for CLI usage
- Author information and contact details
- Package description from README.md
- Repository URL
- Package classifiers for PyPI
- Python version requirements

The script includes helper functions:
- get_requirements(): Reads and parses package dependencies
- get_long_description(): Reads package description from README.md

Requirements:
    Python >= 3.10
    setuptools

Example:
    python setup.py install
"""