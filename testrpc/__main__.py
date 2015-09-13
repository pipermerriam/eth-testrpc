from __future__ import print_function
import argparse
from testrpc import *
from ethereum.tester import accounts
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCRequestHandler

parser = argparse.ArgumentParser(
    description='Simulate an Ethereum blockchain JSON-RPC server.'
)
parser.add_argument('-p', '--port', dest='port', type=int,
                    nargs='?', default=8545)
parser.add_argument('-d', '--domain', dest='domain', type=str,
                    nargs='?', default='localhost')


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


def create_server(host="127.0.0.1", port=8545):
    server = SimpleJSONRPCServer((host, port), SimpleJSONRPCRequestHandlerWithCORS)
    server.register_function(eth_coinbase, 'eth_coinbase')
    server.register_function(eth_accounts, 'eth_accounts')
    server.register_function(eth_gasPrice, 'eth_gasPrice')
    server.register_function(eth_blockNumber, 'eth_blockNumber')
    server.register_function(eth_call, 'eth_call')
    server.register_function(eth_sendTransaction, 'eth_sendTransaction')
    server.register_function(eth_sendRawTransaction, 'eth_sendRawTransaction')
    server.register_function(eth_getCompilers, 'eth_getCompilers')
    server.register_function(eth_compileSolidity, 'eth_compileSolidity')
    server.register_function(eth_getCode, 'eth_getCode')
    server.register_function(eth_getBalance, 'eth_getBalance')
    server.register_function(eth_getTransactionCount, 'eth_getTransactionCount')
    server.register_function(eth_getTransactionByHash, 'eth_getTransactionByHash')
    server.register_function(eth_getTransactionReceipt, 'eth_getTransactionReceipt')
    server.register_function(eth_getBlockByNumber, 'eth_getBlockByNumber')
    server.register_function(eth_newBlockFilter, 'eth_newBlockFilter')
    server.register_function(eth_newFilter, 'eth_newFilter')
    server.register_function(eth_getFilterChanges, 'eth_getFilterChanges')
    server.register_function(eth_getFilterLogs, 'eth_getFilterLogs')
    server.register_function(eth_uninstallFilter, 'eth_uninstallFilter')
    server.register_function(web3_sha3, 'web3_sha3')
    server.register_function(web3_clientVersion, 'web3_clientVersion')
    server.register_function(evm_reset, 'evm_reset')
    server.register_function(evm_snapshot, 'evm_snapshot')
    server.register_function(evm_revert, 'evm_revert')

    return server


def main():
    args = parser.parse_args()

    print web3_clientVersion()

    evm_reset()

    t.set_logging_level(2)
    #slogging.configure(':info,eth.pb:debug,eth.vm.exit:trace')
    #slogging.configure(':info,eth.vm.exit:debug,eth.pb.tx:info')

    print("\nAvailable Accounts\n==================")
    for account in accounts:
        print('0x%s' % account.encode("hex"))

    print("\nListening on %s:%s" % (args.domain, args.port))

    server = create_server(args.domain, args.port)

    server.serve_forever()


if __name__ == "__main__":
    main()
