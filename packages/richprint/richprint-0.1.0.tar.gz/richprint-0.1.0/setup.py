from setuptools import setup, find_packages

setup(
    name = "richprint",
    version = "0.1.0",
    author = "Satyam",
    description = "A styled terminal output wrapper using Rich",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
    packages = find_packages(),
    install_requires = [
        "rich>=13.0.0"
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires = ">=3.7",
)
