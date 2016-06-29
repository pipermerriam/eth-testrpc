import sys
import pkg_resources
import logging

from rlp.utils import decode_hex

from ethereum.utils import (
    sha3,
)
from ethereum.tester import (
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


def eth_call(transaction, block_number="latest"):
    kwargs = {
        TXN_KWARGS_MAP.get(k, k): v for k, v in transaction.items()
    }
    return tester_client.call(**kwargs)


def eth_accounts():
    return tester_client.get_accounts()


def eth_getCompilers():
    return languages.keys()


def eth_compileSolidity(code):
    # TODO: convert to python-solidity lib once it exists
    raise NotImplementedError("This has not yet been implemented")


def eth_getCode(address, block_number="latest"):
    return tester_client.get_code(address, block_number)


def eth_getBalance(address, block_number="latest"):
    return tester_client.get_balance(address, block_number)


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
    # TODO: convert to tester_client once filters implemented
    raise NotImplementedError("This has not yet been implemented")


def eth_newFilter(filter_dict):
    # TODO: convert to tester_client once filters implemented
    raise NotImplementedError("This has not yet been implemented")


def eth_getFilterChanges(filter_id):
    # TODO: convert to tester_client once filters implemented
    raise NotImplementedError("This has not yet been implemented")


def eth_getFilterLogs(filter_id):
    # TODO: convert to tester_client once filters implemented
    raise NotImplementedError("This has not yet been implemented")


def eth_uninstallFilter(filter_id):
    # TODO: convert to tester_client once filters implemented
    raise NotImplementedError("This has not yet been implemented")


RPC_META = {
    'eth_protocolVersion': 63,
    'eth_syncing': False,
    'eth_mining': True,
    'net_version': 1,
    'net_listening': False,
    'net_peerCount': 0,
}


def rpc_configure(key, value):
    RPC_META[key] = value


def eth_protocolVersion():
    return RPC_META['eth_protocolVersion']


def eth_syncing():
    return RPC_META['eth_syncing']


def eth_mining():
    return RPC_META['eth_mining']


def web3_sha3(value):
    logger.info('web3_sha3')
    return encode_32bytes(sha3(decode_hex(strip_0x(value))))


def web3_clientVersion():
    return "TestRPC/" + __version__ + "/python/{v.major}.{v.minor}.{v.micro}".format(
        v=sys.version_info
    )


def net_version():
    return RPC_META['net_version']


def net_listening():
    return RPC_META['net_listening']


def net_peerCount():
    return RPC_META['net_peerCount']
