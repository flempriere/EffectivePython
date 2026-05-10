# setup.py

from setuptools import Extension, setup

setup(
    name="extension2",
    ext_modules=[
        Extension(
            name="extension2",
            sources=["init.c", "extension_2.c"],
        ),
    ],
)
