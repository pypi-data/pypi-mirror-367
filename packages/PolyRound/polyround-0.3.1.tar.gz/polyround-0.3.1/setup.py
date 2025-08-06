# ©2020-​2021 ETH Zurich, Axel Theorell

import os
from setuptools import setup
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PolyRound.version import VERSION

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"), "r"
) as fh:
    long_description = fh.read()

setup(
    name="PolyRound",
    version=VERSION,
    description="A python package for rounding polytopes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/csb.ethz/PolyRound",
    author="Axel Theorell",
    author_email="atheorell@ethz.ch",
    license="GPL-3.0",
    packages=[
        "PolyRound",
        "PolyRound.mutable_classes",
        "PolyRound.static_classes",
        "PolyRound.static_classes.rounding",
    ],
    install_requires=[
        "numpy>=1.2",
        "pandas>=1.2",
        "scipy>=1.4",
        "optlang>=1.4",
    ],
    extras_require={
        "extras": [
            "cobra>=0.20",
            "python-libsbml>=5.18",
            "gurobipy",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
