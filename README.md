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
* `eth_getBalance`
* `eth_gasPrice`
* `eth_blockNumber`
* `eth_sendTransaction`
* `eth_call`
* `web3_sha3`

There’s also a special non-standard method that’s not included within the original RPC specification:

* `evm_reset`

When calling `evm_reset`, the `testrpc` will revert the state of its internal chain back to the genesis block and it will act as if no processing of transactions ever took place. This is useful for automated tests to ensure tests are running against a known clean state.