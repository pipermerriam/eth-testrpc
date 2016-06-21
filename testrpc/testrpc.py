#!/usr/bin/env python

from __future__ import print_function
from __init__ import __version__
from collections import (
    Iterable,
    namedtuple,
)

from rlp.utils import encode_hex, decode_hex

from ethereum import tester as t
from ethereum import utils, transactions, processblock
from ethereum.utils import sha3, rlp
from ethereum.tester import keys, accounts, languages

from utils import decode_number, encode_loglist


############ Default Values / Global Variables ############
evm = None
snapshots = None
transaction_contract_addresses = {}
latest_filter_id = 0
filters = {}
event_log = {}

t.gas_limit = 3141592

############ Snapshots ############

Snapshot = namedtuple("Snapshot", ["block_number", "data"])


############ Filters ############

class BlockFilter(object):
    def __init__(self, evm, from_block_number):
        self.evm = evm
        self._hash_log = []
        self.last_check = from_block_number
        if self.last_check in ['latest', 'pending', 'earliest']:
            self.last_check = self.evm.block.number

    @property
    def logs(self):
        self.getChanges()
        return self._hash_log

    def getChanges(self):
        block_hashes = []
        current_block_number = evm.block.number

        for block_number in range(decode_number(self.last_check), current_block_number):
            block = self.evm.blocks[block_number]
            block_hashes.append('0x' + encode_hex(block.hash))

            if block_number >= len(self._hash_log):
                self._hash_log.append(block_hashes[-1])

        self.last_check = current_block_number
        return block_hashes


# Adapted from http://github.com/ethereum/pyethapp/
class LogFilter(object):
    def __init__(self, evm, filter_dict):
        self.evm = evm
        self.log_dict = {}
        self.filter = filter_dict
        self.topics = filter_dict.get("topics")
        self.addresses = filter_dict.get("addresses")
        self.last_check = filter_dict.get('from_block', 'earliest')

        if self.last_check == 'earliest':
            self.last_check = 0
        elif self.last_check in ['latest', 'pending']:
            self.last_check = self.evm.block.number

    @property
    def logs(self):
        self.getChanges()
        return self.log_dict.values()

    def getChanges(self):
        """Check for logs, return new ones.

        This method walks through the blocks given by :attr:`first_block` and :attr:`last_block`,
        looks at the contained logs, and collects the ones that match the filter.

        :returns: dictionary of new the logs since the last time `getChanges` was called.
        """
        changes = {}
        to_block = self.filter.get('to_block', evm.block.number)
        if to_block in ['latest', 'pending']:
            to_block = self.evm.block.number

        for block_number, events in event_log.items():
            if block_number < self.last_check:
                continue

            if block_number > to_block:
                break

            for event in events:
                if self.topics is not None:
                    topic_match = True
                    if len(event['log'].topics) < len(self.topics):
                        topic_match = False
                    for filter_topic, log_topic in zip(self.topics, event['log'].topics):
                        if filter_topic is not None and filter_topic != log_topic:
                            topic_match = False
                    if not topic_match:
                        continue

                # check for address
                if self.addresses is not None and event['log'].address not in self.addresses:
                    continue

                #id_ = sha3rlp(event['log'])
                changes[event['log_idx']] = event

        self.last_check = self.evm.block.number
        self.log_dict.update(changes)
        return encode_loglist(changes.values())


############ Helper Functions ############

def strip_0x(s):
    if s != None and len(s) > 0 and s[0] == "0" and s[1] == "x":
        s = s[2:]
    return s

def isContract(transaction):
    if type(transaction) is transactions.Transaction:
        return transaction.to == None and transaction.data != None

    if "to" not in transaction and "data" in transaction:
        return True
    else:
        return False

def int_to_hex(int_value):
    encoded = format(int_value, 'x')
    return encoded.zfill(len(encoded)*2 % 2)

def format_block_number(block_number):
    if block_number == "latest" or block_number == "pending":
        block_number = len(evm.blocks) - 1
    elif block_number == "earliest":
        block_number = 0
    else:
        block_number = int(strip_0x(block_number), 16)

    if block_number >= len(evm.blocks):
        return None

    return block_number

class LogListener(object):
    def __init__(self):
        self.log_idx = 0

    def __call__(self, log):
        block = evm.block
        if block.number not in event_log:
            event_log[block.number] = []

        event_log[block.number].append({
            "log": log, "log_idx": self.log_idx,
            "tx_idx": len(block.get_transactions()), "txhash": evm.last_tx.hash,
            "pending": False, "block": block
        })
        self.log_idx += 1

def mine(evm):
    if evm.block.number == 0:
        evm.block.log_listeners.append(LogListener())
    evm.mine()

def jsonTxs(txs):
    return [{
        "from": "0x" + encode_hex(tx._sender),
        "gas": tx.startgas,
        "gasPrice": tx.gasprice,
        "hash": "0x" + encode_hex(tx.hash),
        "input": "0x" + encode_hex(tx.data),
        "nonce": tx.nonce,
        "to": "0x" + encode_hex(tx.to) if tx.to else None,
        "transactionIndex": i,
        "value": tx.value
    } for i, tx in enumerate(txs)]

# Adapted from http://github.com/ethereum/pyethapp/
def decode_filter(filter_dict, block):
    """Decodes a filter as expected by eth_newFilter or eth_getLogs to a :class:`Filter`."""
    if not isinstance(filter_dict, dict):
        raise Exception('Filter must be an object')
    address = filter_dict.get('address', None)
    if utils.is_string(address):
        addresses = [decode_hex(strip_0x(address))]
    elif isinstance(address, Iterable):
        addresses = [decode_hex(strip_0x(addr)) for addr in address]
    elif address is None:
        addresses = None
    else:
        raise Exception('Parameter must be address or list of addresses')
    if 'topics' in filter_dict:
        topics = []
        for topic in filter_dict['topics']:
            if topic is not None:
                topics.append(utils.big_endian_to_int(decode_hex(strip_0x(topic))))
            else:
                topics.append(None)
    else:
        topics = None

    from_block = filter_dict.get('fromBlock') or 'latest'
    to_block = filter_dict.get('toBlock') or 'latest'

    if from_block not in ('earliest', 'latest', 'pending'):
        from_block = decode_number(from_block)

    if to_block not in ('earliest', 'latest', 'pending'):
        to_block = decode_number(to_block)

    # check order
    block_id_dict = {
        'earliest': 0,
        'latest': block.number,
        'pending': block.number+1
    }
    range_ = [b if utils.is_numeric(b) else block_id_dict[b] for b in (from_block, to_block)]
    if range_[0] > range_[1]:
        raise Exception('fromBlock must be newer or equal to toBlock')

    return {"from_block": from_block, "to_block": to_block, "addresses": addresses, "topics": topics}

############ Snapshotting Functions ############

def evm_reset():
    global evm
    global snapshots
    print("Resetting EVM state...")
    evm = t.state()
    snapshots = []
    return True

def evm_snapshot():
    global evm
    global snapshots
    print("Creating snapshot #" + str(len(snapshots)))
    snapshots.append(Snapshot(block_number=evm.block.number, data=evm.snapshot()))
    return "0x" + int_to_hex(len(snapshots) - 1)

def evm_revert(index=None, reset_logs=False):
    global evm
    global snapshots

    if len(snapshots) == 0:
        return False

    if index != None:
        index = int(strip_0x(index), 16)
    else:
        index = len(snapshots) - 1

    print("Reverting snapshot #" + str(index))

    if index >= len(snapshots):
        return False

    snapshot = snapshots[index]

    # print str(snapshot.block_number + 1)
    # print str(len(evm.blocks))

    # Remove all blocks after our saved block number.
    num_blocks = len(evm.blocks)
    del evm.blocks[snapshot.block_number + 1:num_blocks]

    # Revert the evm, taking care to restore our listener
    listener = evm.block.log_listeners.pop(0)
    evm.revert(snapshot.data)
    evm.block.log_listeners.append(listener)

    # Remove any logs from the snapshot block forward
    if reset_logs:
        for i in range(snapshot.block_number+1, num_blocks):
            event_log.pop(i, None)

    # Remove all snapshots after and including this one.
    del snapshots[index:len(snapshots)]
    return True


############ Web3 Functions ############

def eth_coinbase():
    print('eth_coinbase')
    return '0x' + encode_hex(evm.block.coinbase)


def eth_gasPrice():
    print('eth_gasPrice')
    return '0x' + int_to_hex(1)


def eth_blockNumber():
    print('eth_blockNumber')
    return '0x' + int_to_hex(evm.block.number)


def send(transaction):
    if "from" in transaction:
        addr = decode_hex(strip_0x(transaction['from']))
        sender = keys[accounts.index(addr)]
    else:
        sender = keys[0]

    if "value" in transaction:
        value = int(strip_0x(transaction['value']), 16)
    else:
        value = 0

    if "to" in transaction:
        to = strip_0x(transaction['to'])
    else:
        to = None

    if "data" in transaction:
        data = decode_hex(strip_0x(transaction['data']))
    else:
        data = ""

    if "gas" in transaction:
        gas = int(strip_0x(transaction['gas']), 16)
    else:
        gas = None

    # print("value: " + encode_hex(value))
    # print("to: " + to)
    # print("from: " + encode_hex(accounts[keys.index(sender)]))
    # print("data: " + encode_hex(data))
    # print("gas: " + str(gas))

    # Record all logs
    evm.block.log_listeners.append(LogListener())

    if isContract(transaction):
        estimated_cost = len(encode_hex(data)) / 2 * 200

        print("Adding contract...")
        print("Estimated gas cost: " + str(estimated_cost))

        if gas != None and estimated_cost > gas:
            print("* ")
            print("* WARNING: Estimated cost higher than sent gas: " + str(estimated_cost) + " > " + str(gas))
            print("* ")

        r = encode_hex(evm.evm(data, sender, value, gas))
    else:
        r = encode_hex(evm.send(sender, to, value, data))

    r = "0x" + r
    return r


# To mimic a real transaction, we return the transaction hash
# instead of the return value of the transaction.
def eth_sendTransaction(transaction):
    global evm
    global transaction_contract_addresses

    print('eth_sendTransaction')
    r = send(transaction)

    if isContract(transaction):
        contract_address = r
    else:
        contract_address = None

    tx = evm.block.transaction_list[-1]
    tx_hash = "0x" + encode_hex(tx.hash)

    if contract_address != None:
        transaction_contract_addresses[tx_hash] = contract_address

    mine(evm)
    return tx_hash


def eth_sendRawTransaction(raw_tx):
    global evm
    global transaction_contract_addresses

    print('eth_sendRawTransaction')

    # Get a transaction object from the raw hash.
    tx = rlp.decode(decode_hex(strip_0x(raw_tx)), transactions.Transaction)

    print("")
    print("Raw Transaction Details:")
    print("  ")
    print("  From:     " + "0x" + encode_hex(tx.sender))
    print("  To:       " + "0x" + encode_hex(tx.to))
    print("  Gas:      " + int_to_hex(tx.startgas))
    print("  GasPrice: " + int_to_hex(tx.gasprice))
    print("  Value:    " + int_to_hex(tx.value))
    print("  Data:     " + "0x" + encode_hex(tx.data))
    print("")

    (s, r) = processblock.apply_transaction(evm.block, tx)

    if not s:
        raise Exception("Transaction failed")

    if isContract(tx):
        contract_address = r
    else:
        contract_address = None

    tx_hash = "0x" + encode_hex(tx.hash)

    if contract_address != None:
        transaction_contract_addresses[tx_hash] = contract_address

    mine(evm)
    return tx_hash


def eth_call(transaction, block_number):
    print("eth_call")
    snapshot = evm_snapshot()
    r = send(transaction)
    evm_revert(snapshot)
    return r


def eth_accounts():
    r = []
    for index in range(len(accounts)):
        r.append("0x" + encode_hex(accounts[index]))
    return r


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
        "code": '0x' + binary,
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
    address = strip_0x(address)

    block_number = format_block_number(block_number)
    block = evm.blocks[block_number]

    return "0x" + encode_hex(block.get_code(address))


def eth_getBalance(address, block_number="latest"):
    address = strip_0x(address)

    block_number = format_block_number(block_number)
    block = evm.blocks[block_number]

    return "0x" + int_to_hex(block.get_balance(decode_hex(address)))


def eth_getTransactionCount(address, block_number="latest"):
    address = strip_0x(address)

    block_number = format_block_number(block_number)
    block = evm.blocks[block_number]

    return "0x" + int_to_hex(block.get_nonce(decode_hex(address)))


def eth_getTransactionByHash(h):
    h = decode_hex(strip_0x(h))

    total = len(evm.blocks)
    current = total - 1

    tx = None
    tx_index = 0
    block = None

    while current >= 0 and tx == None:
        block = evm.blocks[current]
        tx_index = 0
        for tx in block.get_transactions():
            tx_index += 1
            if tx.hash == h:
                break

        current -= 1

    # Comply with the RPC spec as much as possible.
    # We need to return an object with some things as null.
    if tx == None:
        return {
            "hash": "0x" + encode_hex(h)
        }

    return {
        "hash": "0x" + encode_hex(tx.hash),
        "nonce": "0x" + int_to_hex(tx.nonce),
        "blockHash": "0x" + encode_hex(block.hash),
        "blockNumber": "0x" + int_to_hex(block.number),
        "transactionIndex": "0x" + int_to_hex(tx_index),
        "from": "0x" + encode_hex(tx.sender),
        "to": "0x" + encode_hex(tx.to),
        "value": "0x" + int_to_hex(tx.value),
        "gas": "0x" + int_to_hex(tx.startgas),
        "gasPrice": "0x" + int_to_hex(tx.gasprice),
        "input": "0x" + encode_hex(tx.data)
    }


def eth_getBlockByNumber(block_number, full_tx):
    block_number = format_block_number(block_number)
    #if block_number >= len(
    block = evm.blocks[block_number]

    return {
        "number": "0x" + int_to_hex(block.number),
        "hash": "0x" + encode_hex(block.hash),
        "parentHash": "0x" + encode_hex(block.prevhash),
        "nonce": "0x" + encode_hex(block.nonce),
        "sha3Uncles": "0x" + encode_hex(block.uncles_hash),
        # TODO logsBloom / padding
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "transactionsRoot": "0x" + encode_hex(block.tx_list_root),
        "stateRoot": "0x" + encode_hex(block.state_root),
        "miner": "0x" + encode_hex(block.coinbase),
        "difficulty": "0x" + int_to_hex(block.difficulty),
        # https://github.com/ethereum/pyethereum/issues/266
        # "totalDifficulty": "0x" + int_to_hex(block.chain_difficulty()),
        "size": "0x" + int_to_hex(len(rlp.encode(block))),
        "extraData": "0x" + encode_hex(block.extra_data),
        "gasLimit": "0x" + int_to_hex(block.gas_limit),
        "gasUsed": "0x" + int_to_hex(block.gas_used),
        "timestamp": "0x" + int_to_hex(block.timestamp),
        "transactions": jsonTxs(block.get_transactions()) if full_tx else [encode_hex(tx) for tx in block.get_transaction_hashes()],
        "uncles": block.uncles
    }


def eth_getTransactionReceipt(tx_hash):
    print("eth_getTransactionReceipt")

    global transaction_contract_addresses

    tx_data = eth_getTransactionByHash(tx_hash)
    block_data = eth_getBlockByNumber(tx_data["blockNumber"], False)
    block_number = int(strip_0x(tx_data["blockNumber"]), 16)

    event_logs = {}

    for current_number, events in event_log.items():
        if current_number < block_number:
            continue

        if current_number > block_number:
            break

        for event in events:
           event_logs[event['log_idx']] = event

    return {
        "transactionHash": tx_data["hash"],
        "transactionIndex": tx_data["transactionIndex"],
        "blockNumber": tx_data["blockNumber"],
        "blockHash": tx_data["blockHash"],
        "cumulativeGasUsed": "0x" + int_to_hex(0), #TODO: Make this right.
        "gasUsed": block_data["gasUsed"],
        "contractAddress": transaction_contract_addresses.get(tx_hash, None),
        "logs": encode_loglist(event_logs.values())
    }

def eth_newBlockFilter():
    print("eth_newBlockFilter")

    global filters
    global latest_filter_id
    global evm

    latest_filter_id += 1

    filters[latest_filter_id] = BlockFilter(evm, evm.block.number)

    return "0x" + int_to_hex(latest_filter_id)

def eth_newFilter(filter_dict):
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
    global filters
    global evm

    print("eth_getFilterChanges")

    # Mine a block with every call to getFilterChanges just to
    # ensure block filters will work.
    mine(evm)

    filter_id = int(strip_0x(filter_id), 16)
    return filters[filter_id].getChanges()

def eth_getFilterLogs(filter_id):
    global filters
    global evm

    print("eth_getFilterLogs")
    filter_id = int(strip_0x(filter_id), 16)
    return encode_loglist(filters[filter_id].logs)

def eth_uninstallFilter(filter_id):
    print("eth_uninstallFilter")

    global filters

    filter_id = int(strip_0x(filter_id), 16)

    del filters[filter_id]

    return True

def web3_sha3(argument):
    print('web3_sha3')
    return '0x' + encode_hex(sha3(decode_hex(argument[2:])))


def web3_clientVersion():
    return "Consensys TestRPC/" + __version__ + "/python"
