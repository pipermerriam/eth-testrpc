#!/usr/bin/env python

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from ethereum import tester as t
from rlp.utils import encode_hex
from ethereum.utils import sha3
from ethereum.tester import keys

# CONFIG
BALANCE = 10000000000000000000000
GAS_PRICE = 10000000000000
GAS_LIMIT = 500000000
BLOCK_NUMBER = 1000
LOG_TRANSACTIONS = False
EXECUTE_LOGFILE = False
LOG_FILE = "last_transactions.txt"

# init state
s = t.state()
t.gas_limit = GAS_LIMIT
coinbase = s.block.coinbase

# create contracts
contract = s.abi_contract('contract.se')

# execute transactions
if EXECUTE_LOGFILE:
    transactions = [line.strip().split('\t') for line in open(LOG_FILE) if line]
    for tx in transactions:
        s.send(keys[0], contract.address, int(tx[1]), evmdata=tx[2].decode('hex'))

# log transactions
if LOG_TRANSACTIONS:
    log_file = open(LOG_FILE, 'a+')

print "Ready!"


def int_to_hex(int_value):
    encoded = format(int_value, 'x')
    return encoded.zfill(len(encoded)*2 % 2)


def eth_coinbase():
    print 'eth_coinbase'
    return '0x' + encode_hex(coinbase)


def eth_getBalance(address, block_number):
    print 'eth_getBalance'
    return '0x' + int_to_hex(BALANCE)


def eth_gasPrice():
    print 'eth_gasPrice'
    return '0x' + int_to_hex(GAS_PRICE)


def eth_blockNumber():
    print 'eth_blockNumber'
    return '0x' + int_to_hex(BLOCK_NUMBER)


def eth_call(transaction, block_number):
    print 'eth_call'
    return '0x' + s.send(keys[0], contract.address, 0, evmdata=transaction['data'][2:].decode('hex')).encode('hex')


def eth_sendTransaction(transaction):
    print 'eth_sendTransaction'
    global BALANCE
    global BLOCK_NUMBER
    t.gas_limit = GAS_LIMIT
    value = int(transaction['value'], 16)
    BALANCE -= value
    BLOCK_NUMBER += 1
    if LOG_TRANSACTIONS:
        log_file.write('{}\t{}\t{}\n'.format(contract_address.encode('hex'), value, transaction['data'][2:]))
    s.send(keys[0], contract.address, value, evmdata=transaction['data'][2:].decode('hex'))


def web3_sha3(argument):
    print 'web3_sha3'
    return '0x' + sha3(argument[2:].decode('hex')).encode('hex')


server = SimpleJSONRPCServer(('localhost', 8545))
server.register_function(eth_coinbase, 'eth_coinbase')
server.register_function(eth_getBalance, 'eth_getBalance')
server.register_function(web3_sha3, 'web3_sha3')
server.register_function(eth_gasPrice, 'eth_gasPrice')
server.register_function(eth_blockNumber, 'eth_blockNumber')
server.register_function(eth_call, 'eth_call')
server.register_function(eth_sendTransaction, 'eth_sendTransaction')
server.serve_forever()
