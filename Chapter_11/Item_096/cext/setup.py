# setup.py

from setuptools import Extension, setup

setup(
    name="extension",
    ext_modules=[
        Extension(
            name="extension",
            sources=["init.c", "extension.c"],
        ),
    ],
)
