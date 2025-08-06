###############################################################################
# Coscine Python SDK
# Copyright (c) 2020-2025 RWTH Aachen University
# Licensed under the terms of the MIT License
# For more information on Coscine visit https://www.coscine.de/.
###############################################################################

import setuptools

PROJECT_URL = (
    "https://git.rwth-aachen.de/coscine/community-features/coscine-python-sdk"
)

README = ""

# Read README.md into $description to serve as the long_description on PyPi.
with open("README.md", "rt", encoding="utf-8") as fp:
    README = fp.read()


# Read package metadata into $about
about = {}
with open("src/coscine/__about__.py", "r", encoding="utf-8") as fp:
    exec(fp.read(), about)
__author__ = about["__author__"]
__version__ = about["__version__"]


setuptools.setup(
    name="coscine",
    version=__version__,
    description=(
        "The Coscine Python SDK provides a pythonic high-level "
        "interface to the Coscine REST API."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email="coscine@itc.rwth-aachen.de",
    license="MIT License",
    packages=setuptools.find_packages(where="src"),
    keywords=["Coscine", "RWTH Aachen", "Research Data Management"],
    install_requires=[
        "boto3",
        "isodate",
        "pyshacl",
        "rdflib",
        "requests",
        "requests-cache",
        "requests-toolbelt",
        "tabulate",
        "tqdm"
    ],
    url=PROJECT_URL,
    project_urls={
        "Issues": PROJECT_URL + "/-/issues",
        "Documentation": (
            "https://coscine.pages.rwth-aachen.de/"
            "community-features/coscine-python-sdk/"
        )
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Typing :: Typed"
    ],
    package_dir={"": "src"},
    python_requires=">=3.10"
)
