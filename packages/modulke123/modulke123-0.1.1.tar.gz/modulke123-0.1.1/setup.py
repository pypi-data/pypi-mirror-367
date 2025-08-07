from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="modulke123",
    version="0.1.1",
    author="Your Name",
    author_email="you@example.com",
    description="A test Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Required for README.md
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
