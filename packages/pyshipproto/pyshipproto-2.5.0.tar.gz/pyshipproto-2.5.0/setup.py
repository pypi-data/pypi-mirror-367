
from setuptools import setup, find_packages

VERSION = '2.5.0' 
DESCRIPTION = 'PyShipProto Package'
LONG_DESCRIPTION = 'Pyshipproto package with generated gRPC services.'

# Setting up
setup(
    name="pyshipproto",
    version=VERSION,
    author="PyShipProto",
    author_email="<pyshipproto@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/shipthisco/gRPC-protobuf",
    install_requires=[],
    keywords=['python', 'gRPC', 'protobuf', 'pyshipproto'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
