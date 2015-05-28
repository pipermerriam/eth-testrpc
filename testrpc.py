#!/usr/bin/env python

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from ethereum import tester as t
from rlp.utils import encode_hex
from ethereum import blocks
from ethereum.utils import sha3
from ethereum.tester import keys
from ethereum.tester import accounts
from ethereum.tester import languages
from collections import namedtuple

Snapshot = namedtuple("Snapshot", ["block_number", "data"])

evm = None
snapshots = None

def strip_0x(s):
    if s[0] == "0" and s[1] == "x":
        s = s[2:]
    return s

# Special non-standard function to reset the evm
# state. Useful for automated testing.
def evm_reset():
    global evm
    global snapshots
    print "Resetting EVM state..."
    evm = t.state()
    snapshots = []

def evm_snapshot():
    global evm
    global snapshots
    print "Creating snapshot #" + str(len(snapshots))
    snapshots.append(Snapshot(block_number=evm.block.number, data=evm.snapshot()))
    return "0x" + int_to_hex(len(snapshots) - 1)

def evm_revert(index=None):
    global evm
    global snapshots
    if index != None:
        index = int(strip_0x(index), 16)
    else:
        index = len(snapshots) - 1

    print "Reverting snapshot #" + str(index)

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

# init state
t.set_logging_level(2)
evm_reset()

print "Ready!"


def isContract(transaction):
    if "to" not in transaction and "data" in transaction:
        return True
    else:
        return False


def int_to_hex(int_value):
    encoded = format(int_value, 'x')
    return encoded.zfill(len(encoded)*2 % 2)


def eth_coinbase():
    print 'eth_coinbase'
    return '0x' + encode_hex(evm.block.coinbase)


def eth_gasPrice():
    print 'eth_gasPrice'
    return '0x' + int_to_hex(1)


def eth_blockNumber():
    print 'eth_blockNumber'
    return '0x' + int_to_hex(evm.block.number)


def send(transaction):
    if "from" in transaction:
        addr = strip_0x(transaction['from']).decode("hex")
        sender = keys[accounts.index(addr)]
    else:
        sender = keys[0]

    if "value" in transaction:
        value = transaction['value']
    else:
        value = 0

    if "to" in transaction:
        to = strip_0x(transaction['to'])
    else:
        to = None

    if "data" in transaction:
        data = strip_0x(transaction['data']).decode("hex")
    else:
        data = None
    
    # print "value: " + value.encode("hex")
    # print "to: " + to
    # print "from: " + accounts[keys.index(sender)].encode("hex")
    # print "data: " + data.encode("hex")

    if isContract(transaction):
        print "Adding contract..."
        r = evm.evm(data, sender, value).encode("hex")
    else:
        r = evm.send(sender, to, value, data).encode("hex")
    
    # Remove padded zeroes. 
    # WARNING: This might be super hacky.
    r = "0x" + r.lstrip("0")

    return r


# To mimic a real transaction, we return the transaction hash
# instead of the return value of the transaction. 
def eth_sendTransaction(transaction):
    print 'eth_sendTransaction'
    r = send(transaction)
    evm.mine()

    if isContract(transaction):
        return r
    else:
        tx = evm.last_tx
        return "0x" + tx.hash.encode("hex")
    

def eth_call(transaction, block_number):
    print "eth_call"
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
    contract = combined[len(combined) - 1][1]
    return {
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


# Warning: block.get_code() seems to ignore the block number.
def eth_getCode(address, block_number="latest"): 
    address = strip_0x(address)

    if block_number == "latest" or block_number == "pending":
        block_number = len(evm.blocks) - 1
    elif block_number == "earliest":
        block_number = 0
    else:
        block_number = int(strip_0x(block_number), 16)

    if block_number >= len(evm.blocks):
        return None

    block = evm.blocks[block_number]

    return "0x" + block.get_code(address).encode("hex")


def eth_getTransactionByHash(h):
    h = strip_0x(h).decode("hex")

    total = len(evm.blocks)
    current = total - 1

    tx = None
    tx_index = 0
    block = None

    while current >= 0 and tx == None:
        block = evm.blocks[current]
        if block.includes_transaction(h):
            tx_index = 0
            for tx in block.get_transactions():
                tx_index += 1
                if tx.hash == h:
                    break

        current -= 1

    if tx == None:
        return None

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


def web3_sha3(argument):
    print 'web3_sha3'
    return '0x' + sha3(argument[2:].decode('hex')).encode('hex')


def web3_clientVersion():
    return "Consensys TestRPC/v0.0.1/python"


server = SimpleJSONRPCServer(('localhost', 8545))
server.register_function(eth_coinbase, 'eth_coinbase')
server.register_function(eth_accounts, 'eth_accounts')
server.register_function(eth_gasPrice, 'eth_gasPrice')
server.register_function(eth_blockNumber, 'eth_blockNumber')
server.register_function(eth_call, 'eth_call')
server.register_function(eth_sendTransaction, 'eth_sendTransaction')
server.register_function(eth_getCompilers, 'eth_getCompilers')
server.register_function(eth_compileSolidity, 'eth_compileSolidity')
server.register_function(eth_getCode, 'eth_getCode')
server.register_function(eth_getTransactionByHash, 'eth_getTransactionByHash')
server.register_function(web3_sha3, 'web3_sha3')
server.register_function(web3_clientVersion, 'web3_clientVersion')
server.register_function(evm_reset, 'evm_reset')
server.register_function(evm_snapshot, 'evm_snapshot')
server.register_function(evm_revert, 'evm_revert')
server.serve_forever()
