from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="mrshw",
    version="0.1.0b2",
    author="Barnabás Ifkovics",
    author_email="ifkovics.barnabas@gmail.com",
    description="ctypes-based Python bindings for the mrsh CLI tool",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/w4term3loon/mrsh",
    packages=find_packages(),
    package_data={
        "mrshw": ["libmrsh.so"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

