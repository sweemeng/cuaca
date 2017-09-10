import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Cuaca",
    version = "0.0.2",
    author = "Ng Swee Meng",
    author_email = "sweester@gmail.com",
    description = ("A python wrapper for Malaysian Weather Service API"),
    license = "BSD",
    url = "https://github.com/sweemeng/cuaca",
    packages=['cuaca'],
    long_description=read("README.md"),
    install_requires = [
        'requests',
    ]
)
