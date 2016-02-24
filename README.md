# DEPRECATED

Attention: This project is no longer being maintained. I've focussed my effort on [ethereumjs-testrpc](https://github.com/ethereumjs/testrpc), which is more stable, has more features and is better supported. Please consider using [ethereumjs-testrpc](https://github.com/ethereumjs/testrpc) instead. Note that when switching to [ethereumjs-testrpc](https://github.com/ethereumjs/testrpc), you should uninstall this testrpc first, as they have conflicting binaries. Cheers!

-- Tim Coulter, original dev (@tcoulter)

-----------------------------------

-----------------------------------

-----------------------------------



## Ethereum Test RPC

Limited RPC client intended for use with automated testing. Uses [pythereum](https://github.com/ethereum/pyethereum) to run an Ethereum client behind the scenes without the need for mining or networking. The result is an Ethereum client that provides instant results and quick feedback during development.

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
* `eth_newBlockFilter`
* `eth_newFilter`
* `eth_getFilterChanges`
* `eth_uninstallFilter`
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

So we don't forget. :)

Install `seed` if you haven't already:

```
$ pip install seed
```

Commit any changes you've made first. Then, to make the release:

```
$ seed release
```

Afterward, commit the changes it made for you:

```
git push && git push --tags
```

All done! No need to update a version number.

### License

MIT
