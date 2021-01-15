"""Setup the muffin package."""

from os import path as op

from setuptools import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    install_requires=[
        line for line in _read('requirements.txt').split('\n')
        if line and not line.startswith('#') and not line.startswith('-')
    ],
)
