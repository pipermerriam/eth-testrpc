#!/usr/bin/env python

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from ethereum import tester as t
from rlp.utils import encode_hex
from ethereum.utils import sha3
from ethereum.tester import keys
from ethereum.tester import accounts

# CONFIG
BALANCE = 100000000000000000000000000000

evm = None

# Special non-standard function to reset the evm
# state. Useful for automated testing.
def evm_reset():
    global evm
    print "Resetting EVM state..."
    evm = t.state()

# init state
t.set_logging_level(2)
evm_reset()

print "Ready!"

def strip_0x(s):
    if s[0] == "0" and s[1] == "x":
        s = s[2:]
    return s


def int_to_hex(int_value):
    encoded = format(int_value, 'x')
    return encoded.zfill(len(encoded)*2 % 2)


def eth_coinbase():
    print 'eth_coinbase'
    return '0x' + encode_hex(evm.block.coinbase)


def eth_getBalance(address, block_number):
    print 'eth_getBalance'
    return '0x' + int_to_hex(BALANCE)


def eth_gasPrice():
    print 'eth_gasPrice'
    return '0x' + int_to_hex(1)


def eth_blockNumber():
    print 'eth_blockNumber'
    return '0x' + int_to_hex(evm.block.number)


def send(transaction):
    global BALANCE

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
    
    # print value
    # print to
    # print data.encode("hex")

    BALANCE -= value

    if to == None and data != None:
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
    send(transaction)
    evm.mine()
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


def web3_sha3(argument):
    print 'web3_sha3'
    return '0x' + sha3(argument[2:].decode('hex')).encode('hex')

def web3_clientVersion():
    return "Consensys TestRPC/v0.0.1/python"


server = SimpleJSONRPCServer(('localhost', 8545))
server.register_function(evm_reset, 'evm_reset')
server.register_function(eth_coinbase, 'eth_coinbase')
server.register_function(eth_getBalance, 'eth_getBalance')
server.register_function(eth_accounts, 'eth_accounts')
server.register_function(eth_gasPrice, 'eth_gasPrice')
server.register_function(eth_blockNumber, 'eth_blockNumber')
server.register_function(eth_call, 'eth_call')
server.register_function(eth_sendTransaction, 'eth_sendTransaction')
server.register_function(web3_sha3, 'web3_sha3')
server.register_function(web3_clientVersion, 'web3_clientVersion')
server.serve_forever()
