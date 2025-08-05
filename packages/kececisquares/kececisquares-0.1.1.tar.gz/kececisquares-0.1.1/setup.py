# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kececisquares",
    version="0.1.1",
    description="Keçeci Binomial Squares (Keçeci Binom Kareleri): The Keçeci Binomial Square is a series of binomial coefficients forming a square region within Khayyam (مثلث خیام), Pascal, Binomial Triangle, selected from a specified starting row with defined size and alignment.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mehmet Keçeci",
    maintainer="Mehmet Keçeci",
    author_email="bilginomi@yaani.com",
    maintainer_email="bilginomi@yaani.com",
    url="https://github.com/WhiteSymmetry/kececisquares",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib"
    ],
    extras_require={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    license="MIT",
)
