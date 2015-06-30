#!/usr/bin/env python

from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCRequestHandler
from ethereum import tester as t
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

# Override the SimpleJSONRPCRequestHandler to support access control (*)
class SimpleJSONRPCRequestHandlerWithCORS(SimpleJSONRPCRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # Add these headers to all responses
    def end_headers(self):
        self.send_header("Access-Control-Allow-Headers",
                         "Origin, X-Requested-With, Content-Type, Accept")
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleJSONRPCRequestHandler.end_headers(self)



# Ensure tester.py uses the "official" gas limit.
t.gas_limit = 3141592

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
    return True

def evm_snapshot():
    global evm
    global snapshots
    print "Creating snapshot #" + str(len(snapshots))
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
evm_reset()

t.set_logging_level(2)
#slogging.configure(':info,eth.pb:debug,eth.vm.exit:trace')
#slogging.configure(':info,eth.vm.exit:debug,eth.pb.tx:info')

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
        data = None

    if "gas" in transaction:
        gas = int(strip_0x(transaction['gas']), 16)
    else:
        gas = None

    # print "value: " + value.encode("hex")
    # print "to: " + to
    # print "from: " + accounts[keys.index(sender)].encode("hex")
    # print "data: " + data.encode("hex")
    # print "gas: " + str(gas)

    if isContract(transaction):
        estimated_cost = len(data.encode("hex")) / 2 * 200

        print "Adding contract..."
        print "Estimated gas cost: " + str(estimated_cost)

        if gas != None and estimated_cost > gas:
            print "* "
            print "* WARNING: Estimated cost higher than sent gas: " + str(estimated_cost) + " > " + str(gas)
            print "* "

        r = evm.evm(data, sender, value, gas).encode("hex")
    else:
        r = evm.send(sender, to, value, data, gas).encode("hex")

    r = "0x" + r
    return r


# To mimic a real transaction, we return the transaction hash
# instead of the return value of the transaction.
def eth_sendTransaction(transaction):
    global evm
    print 'eth_sendTransaction'
    r = send(transaction)

    if not isContract(transaction):
        tx = evm.block.transaction_list[-1]
        r = "0x" + tx.hash.encode("hex")

    evm.mine()
    return r


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


def eth_getBalance(address, block_number="latest"):
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

    return "0x" + int_to_hex(block.get_balance(address.decode('hex')))


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
    if block_number == "latest" or block_number == "pending":
        block_number = len(evm.blocks) - 1
    elif block_number == "earliest":
        block_number = 0
    else:
        block_number = int(strip_0x(block_number), 16)

    if block_number >= len(evm.blocks):
        return None

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
        "transactions": block.get_transactions() if full_tx else block.get_transaction_hashes(),
        "uncles": block.uncles
	}


def web3_sha3(argument):
    print 'web3_sha3'
    return '0x' + sha3(argument[2:].decode('hex')).encode('hex')


def web3_clientVersion():
    return "Consensys TestRPC/v0.0.1/python"


server = SimpleJSONRPCServer(('localhost', 8545), SimpleJSONRPCRequestHandlerWithCORS)
server.register_function(eth_coinbase, 'eth_coinbase')
server.register_function(eth_accounts, 'eth_accounts')
server.register_function(eth_gasPrice, 'eth_gasPrice')
server.register_function(eth_blockNumber, 'eth_blockNumber')
server.register_function(eth_call, 'eth_call')
server.register_function(eth_sendTransaction, 'eth_sendTransaction')
server.register_function(eth_getCompilers, 'eth_getCompilers')
server.register_function(eth_compileSolidity, 'eth_compileSolidity')
server.register_function(eth_getCode, 'eth_getCode')
server.register_function(eth_getBalance, 'eth_getBalance')
server.register_function(eth_getTransactionByHash, 'eth_getTransactionByHash')
server.register_function(eth_getBlockByNumber, 'eth_getBlockByNumber')
server.register_function(web3_sha3, 'web3_sha3')
server.register_function(web3_clientVersion, 'web3_clientVersion')
server.register_function(evm_reset, 'evm_reset')
server.register_function(evm_snapshot, 'evm_snapshot')
server.register_function(evm_revert, 'evm_revert')
server.serve_forever()
