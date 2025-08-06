from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="extraction-triangle",
    version="0.1.0",
    author="barnobarno666",
    author_email="barnobarnobarno666@gmail.com",
    description="A Python library for creating right triangle plots for partially miscible extraction (for wankat book)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barnobarno666/extraction-triangle",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.18.0",
        "matplotlib>=3.3.0",
        "scipy>=1.5.0",
    ],
)
