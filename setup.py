"""An Ethereum client simulator that provides instant results and quick
feedback during development involving smart contracts.

https://github.com/pipermerriam/eth-testrpc
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eth-testrpc',
    version="0.9.1",
    description='An Ethereum simulator for aiding smart contract development.',
    long_description=long_description,
    url='https://github.com/pipermerriam/eth-testrpc',
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='ethereum blockchain development testing',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        "gevent>=1.1.2",
        'Werkzeug>=0.11.10',
        'click>=6.6',
        'ethereum>=1.5.2',
        'json-rpc>=1.10.3',
        'rlp>=0.4.4,<0.4.7',
    ],
    entry_points={
        'console_scripts': [
            'testrpc-py=testrpc.cli:runserver',
        ],
    }
)
