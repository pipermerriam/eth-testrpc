# Ethereum Test RPC server

[![Join the chat at https://gitter.im/pipermerriam/eth-testrpc](https://badges.gitter.im/pipermerriam/eth-testrpc.svg)](https://gitter.im/pipermerriam/eth-testrpc?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

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
* `eth_protocolVersion` ( see `rpc_configure`)
* `eth_syncing` ( see `rpc_configure`)
* `eth_mining` ( see `rpc_configure`)
* `web3_sha3`
* `web3_clientVersion`
* `net_version` (see `rpc_configure`)
* `net_listening` (see `rpc_configure`)
* `net_peerCount` (see `rpc_configure`)

There’s also special non-standard methods that aren’t included within the original RPC specification:

* `evm_reset` : No params, no return value.
* `evm_snapshot` : No params. Returns the integer id of the snapshot created.
* `evm_revert` : One optional param. Reverts to the snapshot id passed, or the latest snapshot.

When calling `evm_reset`, the `testrpc` will revert the state of its internal
chain back to the genesis block and it will act as if no processing of
transactions has taken place. Similarly, you can use `evm_snapshot` and
`evm_revert` methods to save and restore the evm state as desired. Example use
cases for these methods are as follows:

* `evm_reset` : Run once at the beginning of your test suite.
* `evm_snapshot` : Run at the beginning of each test, snapshotting the state of the evm.
* `evm_revert` : Run at the end of each test, reverting back to a known clean state.

TestRPC also exposes the `evm_mine` method for advancing the test evm by a
single block.

* `evm_mine` : No params, no return value.

TestRPC exposes the `rpc_configure` method which can be used to modify the
static values returned by the following endpoints.

* `eth_protocolVersion` (default `63`)
* `eth_syncing` (default `False`)
* `eth_mining` (default `True`)
* `net_version` (default `1`)
* `net_listening` (default `False`)
* `net_peerCount` (default `0`)
* `homestead_block_number` (default `0`)
* `dao_fork_block_number` (default `0`)

The `rpc_configure` takes two parameters.

* `key`: string representing the rpc method on which you want to change the return value.
* `value`: the value that should be returned by the endpoint.

The `homestead` and `dao` fork configurations determine which block number the
fork rules should come into effect.  Both default to `0`.


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
