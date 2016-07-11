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
    version="0.4.2",
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
        'Werkzeug>=0.11.10',
        'json-rpc>=1.10.3',
        # TODO: bump this once the next version of pyethereum is released.
        'ethereum>=1.3.6',
        'rlp>=0.4.4',
        'ethereum-tester-client>=0.4.0',
    ],
    entry_points={
        'console_scripts': [
            'testrpc=testrpc.__main__:main',
        ],
    }
)
