# Ethereum Test RPC server

## Ethereum Test RPC

Limited RPC client intended for use with automated testing. Uses
[pythereum](https://github.com/ethereum/pyethereum) to run an Ethereum client
behind the scenes without the need for mining or networking. The result is an
Ethereum client that provides instant results and quick feedback during
development.

### Install

Installing is easy, through pip:

```
$ pip install eth-testrpc
```

Or, to upgrade:

```
pip install eth-testrpc --upgrade
```

### Run

Installing through pip will make the `testrpc` command available on your machine:

```
$ testrpc
```

This will run testrpc on localhost:8545. You can pass through a different port (-p, --port) or domain (-d, --domain).

### Implemented methods

The RPC methods currently implemented are:

* `eth_coinbase`
* `eth_accounts`
* `eth_gasPrice`
* `eth_blockNumber`
* `eth_sendTransaction`
* `eth_sendRawTransaction`
* `eth_call`
* `eth_getCompilers`
* `eth_compileSolidity`
* `eth_getCode` (only supports block number “latest”)
* `eth_getBalance`
* `eth_getTransactionCount`
* `eth_getTransactionByHash`
* `eth_getTransactionReceipt`
* `eth_newBlockFilter`  (temporarily removed until implemented in underlying library)
* `eth_newFilter`  (temporarily removed until implemented in underlying library)
* `eth_getFilterChanges`  (temporarily removed until implemented in underlying library)
* `eth_uninstallFilter`  (temporarily removed until implemented in underlying library)
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


### Releasing a new version (for eth-testrpc developers)


* Bump version number in `setup.py`
* Add entry to `CHANGES.txt`
* Tag the release.

```
git tag -s -m "X.X.X Release" vX.X.X
git push --tags
```

* Go make the release on github for the tag you just pushed
* Build and push release to PyPI

```
make release
```


### License

MIT


### Consensys

This library was originally authored by Consensys and transferred later when it
was no longer maintained.  A big thanks for them to creating this extremely
useful library.
