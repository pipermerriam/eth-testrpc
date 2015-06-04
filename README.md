## Test RPC

Limited RPC client intended for use with automated testing. Uses [pythereum](https://github.com/ethereum/pyethereum) to run an Ethereum client behind the scenes without the need for mining or networking. The result is an Ethereum client that provides instant results and quick feedback during development.

### Install

To install `testrpc`, follow these steps. It’s recommended you perform these within a virtualenv.

1. `$ git clone https://github.com/Consensys/testrpc` (clone this repository)
2. `cd testrpc`
3. `$ pip install -r requirements.txt`

### Run

`cd` into your clone of this repository, then type:

```
$ python testrpc.py
```

### Implemented methods

The RPC methods currently implemented are:

* `eth_coinbase`
* `eth_accounts`
* `eth_gasPrice`
* `eth_blockNumber`
* `eth_sendTransaction`
* `eth_call`
* `eth_getCompilers`
* `eth_compileSolidity`
* `eth_getCode` (only supports block number “latest”)
* `eth_getTransactionByHash`
* `web3_sha3`
* `web3_clientVersion`

There’s also special non-standard methods that aren’t included within the original RPC specification:

* `evm_reset` : No params, no return value.
* `evm_snapshot` : No params. Returns the integer id of the snapshot created.
* `evm_revert` : One optional param. Reverts to the snapshot id passed, or the latest snapshot.

When calling `evm_reset`, the `testrpc` will revert the state of its internal chain back to the genesis block and it will act as if no processing of transactions has taken place. Similarly, you can use `evm_snapshot` and `evm_revert` methods to save and restore the evm state as desired. Example use cases for these methods are as follows:

* `evm_reset` : Run once at the beginning of your test suite. 
* `evm_snapshot` : Run at the beginning of each test, snapshotting the state of the evm.
* `evm_revert` : Run at the end of each test, reverting back to a known clean state.

### License

MIT
