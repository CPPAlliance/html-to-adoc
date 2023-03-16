from setuptools import setup

setup(
    name="convert",
    version="0.0.1",
    py_modules=["convert"],
    install_requires=[
        "Click>=8.1.3",
    ],
    entry_points={
        "console_scripts": [
            "convert = main:cli",
        ],
    },
)
