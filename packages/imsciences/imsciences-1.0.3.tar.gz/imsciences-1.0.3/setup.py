import sys
from pathlib import Path

from setuptools import find_packages, setup

# Constants
MAX_PATCH_VERSION = 10  # Maximum patch version before incrementing minor


def read_md(file_name):
    """Read markdown file content."""
    try:
        with Path(file_name).open(encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_version():
    """Get version from __init__.py file."""
    with Path("imsciences/__init__.py").open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.2"  # Start from 1.0.0 instead of 0.0.0


def increment_version():
    """Increment version in __init__.py file with simple versioning."""
    init_file = Path("imsciences/__init__.py")

    # Read the file
    content = init_file.read_text(encoding="utf-8")

    # Find current version
    current_version = get_version()

    # Parse version
    parts = current_version.split(".")
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    # Increment patch
    patch += 1

    # If patch reaches maximum, reset to 0 and increment minor
    if patch >= MAX_PATCH_VERSION:
        patch = 0
        minor += 1

    new_version = f"{major}.{minor}.{patch}"

    # Replace version in file
    new_content = content.replace(
        f'__version__ = "{current_version}"',
        f'__version__ = "{new_version}"',
    ).replace(
        f"__version__ = '{current_version}'",
        f"__version__ = '{new_version}'",
    )

    # Write back to file
    init_file.write_text(new_content, encoding="utf-8")

    print(f"Version incremented from {current_version} to {new_version}")
    return new_version


# Only increment when building (not when just importing)
if len(sys.argv) > 1 and (
    "sdist" in sys.argv or "bdist_wheel" in sys.argv or "upload" in sys.argv
):
    VERSION = increment_version()
else:
    VERSION = get_version()

DESCRIPTION = "IMS Data Processing Package"
LONG_DESCRIPTION = read_md("README.md")

# Setting up
setup(
    name="imsciences",
    version=VERSION,
    author="IMS",
    author_email="cam@im-sciences.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        "pandas",
        "plotly",
        "numpy",
        "fredapi",
        "xgboost",
        "scikit-learn",
        "bs4",
        "yfinance",
        "holidays",
        "google-analytics-data",
        "geopandas",
        "geopy",
        "workalendar",
    ],
    keywords=[
        "data processing",
        "apis",
        "data analysis",
        "data visualization",
        "machine learning",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
