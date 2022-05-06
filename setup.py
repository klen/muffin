"""Setup the package."""

# Parse requirements
# ------------------
import pathlib

import pkg_resources


def parse_requirements(path: str) -> "list[str]":
    with pathlib.Path(path).open() as requirements:
        return [str(req) for req in pkg_resources.parse_requirements(requirements)]


# Setup package
# -------------
from setuptools import setup

setup(
    install_requires=parse_requirements("requirements/requirements.txt"),
    extras_require={
        "standard": parse_requirements("requirements/requirements-standard.txt"),
        "tests": parse_requirements("requirements/requirements-tests.txt"),
        "build": ["bump2version", "wheel"],
        "docs": parse_requirements("requirements/requirements-docs.txt"),
    },
)

# pylama:ignore=E402,D
