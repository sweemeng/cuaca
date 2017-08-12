import os
from setuptools import setup


setup(
    name = "Cuaca",
    version = "0.0.1",
    author = "Ng Swee Meng",
    author_email = "sweester@gmail.com",
    description = ("A python wrapper for Malaysian Weather Service API"),
    license = "BSD",
    url = "https://github.com/sweemeng/cuaca",
    packages=['cuaca'],
    long_description="This is a Wrapper for the Malaysian Weather Service API",
    install_requires = [
        'requests',
    ]
)
