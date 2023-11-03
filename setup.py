from setuptools import setup, find_packages
from datetime import date


def readme():
    with open("README.md") as f:
        return f.read()


def version():
    with open("rosh/__init__.py") as fd:
        for line in fd:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


def install_requires():
    requires = [
        "cachetools",
        "prettytable",
        "prompt_toolkit",
        "pyroute2",
        "fuzzyfinder",
        "setproctitle"
    ]

    return requires


setup(
    name="rosh",
    version=version(),
    description="router shell is a interactive diagnostic shell for Linux",
    author="Thomas Liske",
    author_email="thomas@fiasko-nw.net",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://codeberg.org/liske/rosh",
    license="GPL3+",
    packages=find_packages(),
    install_requires=install_requires(),
    extras_require={
        'ifstate': [
            'ifstate'
        ]
    },
    entry_points={
        "console_scripts": ["rosh = rosh:main"]
    },
)
