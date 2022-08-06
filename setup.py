import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Cuaca",
    version = "0.1.0",
    author = "Ng Swee Meng",
    author_email = "sweester@gmail.com",
    description = ("A python wrapper for Malaysian Weather Service API"),
    license = "BSD",
    url = "https://github.com/sweemeng/cuaca",
    packages=['cuaca'],
    long_description=read("README.md"),
    long_description_content_type='text/markdown',
    install_requires = [
        'requests',
    ]
)
