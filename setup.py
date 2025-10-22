from setuptools import setup, find_packages

setup(
    name='RemoteBlobStore',
    version='1.0.4',
    description='Python library for accessing cloud files',
    url='https://github.com/markusmobius/newsprinceton-pythoncloud',
    packages=find_packages(),
    package_data={'': ['Remote/RemoteBlobServer.zip']},
    include_package_data=True
)