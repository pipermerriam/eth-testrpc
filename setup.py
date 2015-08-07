"""An Ethereum client simulator that provides instant results and quick
feedback during development involving smart contracts.

https://github.com/ConsenSys/eth-testrpc
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='eth-testrpc',
    version='0.1.4',
    description='An Ethereum simulator for aiding smart contract development.',
    long_description=long_description,
    url='https://github.com/ConsenSys/eth-testrpc',
    download_url='https://github.com/Consensys/eth-testrpc/tarball/v0.1.4',
    author='ConsenSys',
    author_email='info@consensys.net',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='ethereum blockchain development testing',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'jsonrpclib',
        'serpent',
        'ethereum',
    ],
    entry_points={
        'console_scripts': [
            'testrpc=testrpc.__main__',
        ],
    },
)
