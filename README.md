## Test RPC

Limited RPC client intended for use with automated testing. Uses [pythereum](https://github.com/ethereum/pyethereum) to run an Ethereum client behind the scenes without the need for mining or networking. The result is an Ethereum client that provides instant results and quick feedback during development.

### Install

To install `testrpc`, follow these steps. It’s recommended you perform these within a virtualenv.

1. `$ git clone https://github.com/Consensys/testrpc` (clone this repository)
2. `$ git clone https://github.com/ethereum/pyethereum` (doesn’t need to be inside the clone of this responsitory)
3. `$ cd pythereum`
4. `$ python setup.py install`

There’s nothing more to install beyond `pythereum`.

### Run

`cd` into your clone of this repository, then type:

```
$ python testrpc.py
```

### Implemented methods

The RPC methods currently implemented are:

* `eth_coinbase`
* `eth_accounts`
* `eth_getBalance`
* `eth_gasPrice`
* `eth_blockNumber`
* `eth_sendTransaction`
* `eth_call`
* `web3_sha3`
* `web3_clientVersion`

There’s also a special non-standard method that’s not included within the original RPC specification:

* `evm_reset`

When calling `evm_reset`, the `testrpc` will revert the state of its internal chain back to the genesis block and it will act as if no processing of transactions ever took place. This is useful for automated tests to ensure tests are running against a known clean state.

### License

MIT

```
Copyright (c) 2015 Consensys Systems LLC and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```