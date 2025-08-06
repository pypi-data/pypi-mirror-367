from setuptools import find_packages, setup


CLASSIFIERS = [
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.10",
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="fxc_logger",
    packages=find_packages(include=["fxc_logger"]),
    version="1.0.2",
    description="Python library for logging with colors and http status code.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frexco-digital/fxc-logger.git",
    install_requires=["requests"],
    classifiers=CLASSIFIERS,
    keywords="logs logging logger",
)
