#!/usr/bin/env python

from __future__ import print_function
import pkg_resources
import logging

from rlp.utils import encode_hex, decode_hex

from ethereum.utils import (
    sha3,
)
from ethereum.tester import (
    accounts,
    languages,
)

from eth_tester_client import EthTesterClient
from eth_tester_client.utils import (
    strip_0x,
    encode_number,
    encode_32bytes,
)


__version__ = pkg_resources.get_distribution("eth-testrpc").version


logger = logging.getLogger(__name__)


#
# Global Client
#
tester_client = EthTesterClient()


#
# Snapshot and Reset
#
def evm_reset():
    tester_client.reset_evm()
    return True


def evm_snapshot():
    snapshot_idx = tester_client.snapshot_evm()
    return encode_number(snapshot_idx)


def evm_revert(snapshot_idx=None):
    try:
        tester_client.revert_evm(snapshot_idx)
    except ValueError:
        return False
    else:
        return True


#
#  Web3 Functions
#
def eth_coinbase():
    logger.info('eth_coinbase')
    return tester_client.get_coinbase()


def eth_gasPrice():
    logger.info('eth_gasPrice')
    return encode_number(tester_client.get_gas_price())


def eth_blockNumber():
    logger.info('eth_blockNumber')
    return encode_number(tester_client.get_block_number())


TXN_KWARGS_MAP = {
    'from': '_from',
}


def eth_sendTransaction(transaction):
    kwargs = {
        TXN_KWARGS_MAP.get(k, k): v for k, v in transaction.items()
    }
    return tester_client.send_transaction(**kwargs)


def eth_sendRawTransaction(raw_tx):
    return tester_client.send_raw_transaction(raw_tx)


def eth_call(transaction, block_number):
    print("eth_call")
    snapshot = evm_snapshot()
    r = send(transaction)
    evm_revert(snapshot)
    return r


def eth_accounts():
    return [add_0x(encode_hex(acct)) for acct in accounts]


def eth_getCompilers():
    return languages.keys()


def eth_compileSolidity(code):
    combined = languages["solidity"].combined(code)
    name = combined[len(combined) - 1][0]
    contract = combined[len(combined) - 1][1]
    val = {}

    # Support old and new versions of solc
    if "binary" in contract:
        binary = contract['binary']
    else:
        binary = contract['bin']

    if "json-abi" in contract:
        abi = contract['json-abi']
    else:
        abi = contract['abi']

    val[name] = {
        "code": add_0x(binary),
        "info": {
            "source": code,
            "language": "Solidity",
            "languageVersion": "0",
            "compilerVersion": "0",
            "abiDefinition": abi,
            "userDoc": {
                "methods": {}
            },
            "developerDoc": {
                "methods": {}
            }
        }
    }
    return val


# Warning: block.get_code() seems to ignore the block number.
def eth_getCode(address, block_number="latest"):
    return client.get_code(address, block_number)


def eth_getBalance(address, block_number="latest"):
    return client.get_balance(address, block_number)


def eth_getTransactionCount(address, block_number="latest"):
    return encode_number(tester_client.get_transaction_count(address, block_number))


def eth_getTransactionByHash(tx_hash):
    try:
        return tester_client.get_transaction_by_hash(tx_hash)
    except ValueError:
        return None


def eth_getBlockByHash(block_hash, full_tx=True):
    return tester_client.get_block_hash(block_hash, full_tx)


def eth_getBlockByNumber(block_number, full_tx=True):
    return tester_client.get_block_number(block_number, full_tx)


def eth_getTransactionReceipt(tx_hash):
    try:
        return tester_client.get_transaction_receipt(tx_hash)
    except ValueError:
        return None


def eth_newBlockFilter():
    # TODO: convert to tester_client
    print("eth_newBlockFilter")

    global filters
    global latest_filter_id
    global evm

    latest_filter_id += 1

    filters[latest_filter_id] = BlockFilter(evm, evm.block.number)

    return "0x" + int_to_hex(latest_filter_id)


def eth_newFilter(filter_dict):
    # TODO: convert to tester_client
    print("eth_newFilter")

    global filters
    global latest_filter_id
    global evm

    latest_filter_id += 1
    filters[latest_filter_id] = LogFilter(evm, decode_filter(filter_dict, evm.block))
    int_to_hex(latest_filter_id)

    for x in filters.values():
        if not hasattr(x, 'topics'):
            continue

    return "0x" + int_to_hex(latest_filter_id)


def eth_getFilterChanges(filter_id):
    # TODO: convert to tester_client
    global filters
    global evm

    print("eth_getFilterChanges")

    # Mine a block with every call to getFilterChanges just to
    # ensure block filters will work.
    mine(evm)

    filter_id = int(strip_0x(filter_id), 16)
    return filters[filter_id].getChanges()


def eth_getFilterLogs(filter_id):
    # TODO: convert to tester_client
    global filters
    global evm

    print("eth_getFilterLogs")
    filter_id = int(strip_0x(filter_id), 16)
    return encode_loglist(filters[filter_id].logs)


def eth_uninstallFilter(filter_id):
    # TODO: convert to tester_client
    print("eth_uninstallFilter")

    global filters

    filter_id = int(strip_0x(filter_id), 16)

    del filters[filter_id]

    return True


def web3_sha3(value):
    print('web3_sha3')
    return encode_32bytes(sha3(decode_hex(strip_0x(value))))


def web3_clientVersion():
    return "TestRPC/" + __version__ + "/python"
