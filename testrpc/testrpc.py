#!/usr/bin/env python

from __future__ import print_function
from ethereum import tester as t
from rlp.sedes import big_endian_int, binary
from rlp.utils import encode_hex
from ethereum import blocks
from ethereum import utils
from ethereum import transactions
from ethereum import processblock
from ethereum.utils import sha3
from ethereum.utils import rlp
from ethereum.tester import keys
from ethereum.tester import accounts
from ethereum.tester import languages
from collections import namedtuple
from ethereum import slogging


############ Default Values / Global Variables ############
evm = None
snapshots = None
transaction_contract_addresses = {}
latest_filter_id = 0
filters = {}

t.gas_limit = 3141592

############ Snapshots ############

Snapshot = namedtuple("Snapshot", ["block_number", "data"])


############ Filters ############

BlockFilter = namedtuple("BlockFilter", ["block_number"])


############ Helper Functions ############

def strip_0x(s):
    if s[0] == "0" and s[1] == "x":
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

def evm_revert(index=None):
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
    del evm.blocks[snapshot.block_number + 1:len(evm.blocks)]

    # Revert the evm
    evm.revert(snapshot.data)

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
        addr = strip_0x(transaction['from']).decode("hex")
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
        data = strip_0x(transaction['data']).decode("hex")
    else:
        data = ""

    if "gas" in transaction:
        gas = int(strip_0x(transaction['gas']), 16)
    else:
        gas = None

    # print("value: " + value.encode("hex"))
    # print("to: " + to)
    # print("from: " + accounts[keys.index(sender)].encode("hex"))
    # print("data: " + data.encode("hex"))
    # print("gas: " + str(gas))

    if isContract(transaction):
        estimated_cost = len(data.encode("hex")) / 2 * 200

        print("Adding contract...")
        print("Estimated gas cost: " + str(estimated_cost))

        if gas != None and estimated_cost > gas:
            print("* ")
            print("* WARNING: Estimated cost higher than sent gas: " + str(estimated_cost) + " > " + str(gas))
            print("* ")

        r = evm.evm(data, sender, value, gas).encode("hex")
    else:
        r = evm.send(sender, to, value, data, gas).encode("hex")

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
    tx_hash = "0x" + tx.hash.encode("hex")

    if contract_address != None:
        transaction_contract_addresses[tx_hash] = contract_address

    evm.mine()
    return tx_hash


def eth_sendRawTransaction(raw_tx):
    global evm
    global transaction_contract_addresses

    print('eth_sendRawTransaction')

    # Get a transaction object from the raw hash.
    tx = rlp.decode(strip_0x(raw_tx).decode("hex"), transactions.Transaction)

    print("")
    print("Raw Transaction Details:")
    print("  ")
    print("  From:     " + "0x" + tx.sender.encode("hex"))
    print("  To:       " + "0x" + tx.to.encode("hex"))
    print("  Gas:      " + int_to_hex(tx.startgas))
    print("  GasPrice: " + int_to_hex(tx.gasprice))
    print("  Value:    " + int_to_hex(tx.value))
    print("  Data:     " + "0x" + tx.data.encode("hex"))
    print("")

    (s, r) = processblock.apply_transaction(evm.block, tx)

    if not s:
        raise Exception("Transaction failed")

    if isContract(tx):
        contract_address = r
    else:
        contract_address = None

    tx_hash = "0x" + tx.hash.encode("hex")

    if contract_address != None:
        transaction_contract_addresses[tx_hash] = contract_address

    evm.mine()
    return tx_hash


def eth_call(transaction, block_number):
    print("eth_call")
    snapshot = evm.snapshot()
    r = send(transaction)
    evm.revert(snapshot)
    return r


def eth_accounts():
    r = []
    for index in range(len(accounts)):
        r.append("0x" + accounts[index].encode("hex"))
    return r


def eth_getCompilers():
    return languages.keys()


def eth_compileSolidity(code):
    combined = languages["solidity"].combined(code)
    name = combined[len(combined) - 1][0]
    contract = combined[len(combined) - 1][1]
    val = {}
    val[name] = {
        "code": '0x' + contract['binary'],
        "info": {
            "source": code,
            "language": "Solidity",
            "languageVersion": "0",
            "compilerVersion": "0",
            "abiDefinition": contract['json-abi'],
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

    return "0x" + block.get_code(address).encode("hex")


def eth_getBalance(address, block_number="latest"):
    address = strip_0x(address)

    block_number = format_block_number(block_number)
    block = evm.blocks[block_number]

    return "0x" + int_to_hex(block.get_balance(address.decode('hex')))


def eth_getTransactionCount(address, block_number="latest"):
    address = strip_0x(address)

    block_number = format_block_number(block_number)
    block = evm.blocks[block_number]

    return "0x" + int_to_hex(block.get_nonce(address.decode('hex')))


def eth_getTransactionByHash(h):
    h = strip_0x(h).decode("hex")

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
            "hash": "0x" + h.encode("hex")
        }

    return {
        "hash": "0x" + tx.hash.encode("hex"),
        "nonce": "0x" + int_to_hex(tx.nonce),
        "blockHash": "0x" + block.hash.encode("hex"),
        "blockNumber": "0x" + int_to_hex(block.number),
        "transactionIndex": "0x" + int_to_hex(tx_index),
        "from": "0x" + tx.sender.encode("hex"),
        "to": "0x" + tx.to.encode("hex"),
        "value": "0x" + int_to_hex(tx.value),
        "gas": "0x" + int_to_hex(tx.startgas),
        "gasPrice": "0x" + int_to_hex(tx.gasprice),
        "input": "0x" + tx.data.encode("hex")
    }


def eth_getBlockByNumber(block_number, full_tx):
    block_number = format_block_number(block_number)
    #if block_number >= len(
    block = evm.blocks[block_number]

    return {
        "number": "0x" + int_to_hex(block.number),
        "hash": "0x" + block.hash.encode('hex'),
        "parentHash": "0x" + block.prevhash.encode('hex'),
        "nonce": "0x" + block.nonce.encode('hex'),
        "sha3Uncles": "0x" + block.uncles_hash.encode('hex'),
        # TODO logsBloom / padding
        "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "transactionsRoot": "0x" + block.tx_list_root.encode('hex'),
        "stateRoot": "0x" + block.state_root.encode('hex'),
        "miner": "0x" + block.coinbase.encode('hex'),
        "difficulty": "0x" + int_to_hex(block.difficulty),
        # https://github.com/ethereum/pyethereum/issues/266
        # "totalDifficulty": "0x" + int_to_hex(block.chain_difficulty()),
        "size": "0x" + int_to_hex(len(rlp.encode(block))),
        "extraData": "0x" + block.extra_data.encode('hex'),
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

    return {
        "transactionHash": tx_data["hash"],
        "transactionIndex": tx_data["transactionIndex"],
        "blockNumber": tx_data["blockNumber"],
        "blockHash": tx_data["blockHash"],
        "cumulativeGasUsed": "0x" + int_to_hex(0), #TODO: Make this right.
        "gasUsed": block_data["gasUsed"],
        "contractAddress": transaction_contract_addresses.get(tx_hash, None)
    }

def eth_newBlockFilter():
    print("eth_newBlockFilter")

    global filters
    global latest_filter_id
    global evm

    latest_filter_id += 1

    filters[latest_filter_id] = BlockFilter(evm.block.number)

    return "0x" + int_to_hex(latest_filter_id)

def eth_getFilterChanges(filter_id):
    global filters
    global evm

    print("eth_getFilterChanges")

    # Mine a block with every call to getFilterChanges just to
    # ensure block filters will work.
    evm.mine()

    filter_id = int(strip_0x(filter_id), 16)

    block_filter = filters[filter_id]

    old_block_number = block_filter.block_number
    current_block_number = evm.block.number

    block_hashes = []

    for block_number in range(old_block_number, current_block_number):
        block = evm.blocks[block_number]
        block_hashes.append('0x' + block.hash.encode('hex'))

    # Update the block filter with the current block
    filters[filter_id] = BlockFilter(current_block_number)

    return block_hashes

def eth_uninstallFilter(filter_id):
    print("eth_uninstallFilter")

    global filters

    filter_id = int(strip_0x(filter_id), 16)

    del filters[filter_id]

    return True

def web3_sha3(argument):
    print('web3_sha3')
    return '0x' + sha3(argument[2:].decode('hex')).encode('hex')


def web3_clientVersion():
    return "Consensys TestRPC/v0.0.2/python"
