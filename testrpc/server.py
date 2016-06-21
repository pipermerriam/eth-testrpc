import functools
from threading import Lock

from werkzeug.wrappers import Request, Response

from jsonrpc import JSONRPCResponseManager, dispatcher

from . import testrpc


RESPONSE_HEADERS = {
    "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
    "Access-Control-Allow-Origin": "*",
}

# When calling server.register_function, first wrap the function in a mutex.
# This has the effect of serializing all RPC calls. Although we use a
# multithreaded HTTP server, the EVM itself is not thread-safe, so we must take
# care when interacting with it.
evm_lock = Lock()


def with_lock(rpc_fn):
    @functools.wraps(rpc_fn)
    def inner(*args, **kwargs):
        evm_lock.acquire()
        try:
            return rpc_fn(*args, **kwargs)
        finally:
            evm_lock.release()

    return inner


def add_method_with_lock(rpc_fn, *args, **kwargs):
    rpc_fn_with_lock = with_lock(rpc_fn)
    return dispatcher.add_method(rpc_fn_with_lock, *args, **kwargs)


add_method_with_lock(testrpc.eth_coinbase, 'eth_coinbase')
add_method_with_lock(testrpc.eth_accounts, 'eth_accounts')
add_method_with_lock(testrpc.eth_gasPrice, 'eth_gasPrice')
add_method_with_lock(testrpc.eth_blockNumber, 'eth_blockNumber')
add_method_with_lock(testrpc.eth_call, 'eth_call')
add_method_with_lock(testrpc.eth_sendTransaction, 'eth_sendTransaction')
add_method_with_lock(testrpc.eth_sendRawTransaction, 'eth_sendRawTransaction')
add_method_with_lock(testrpc.eth_getCompilers, 'eth_getCompilers')
add_method_with_lock(testrpc.eth_compileSolidity, 'eth_compileSolidity')
add_method_with_lock(testrpc.eth_getCode, 'eth_getCode')
add_method_with_lock(testrpc.eth_getBalance, 'eth_getBalance')
add_method_with_lock(testrpc.eth_getTransactionCount, 'eth_getTransactionCount')
add_method_with_lock(testrpc.eth_getTransactionByHash, 'eth_getTransactionByHash')
add_method_with_lock(testrpc.eth_getTransactionReceipt, 'eth_getTransactionReceipt')
add_method_with_lock(testrpc.eth_getBlockByNumber, 'eth_getBlockByNumber')
add_method_with_lock(testrpc.eth_newBlockFilter, 'eth_newBlockFilter')
add_method_with_lock(testrpc.eth_newFilter, 'eth_newFilter')
add_method_with_lock(testrpc.eth_getFilterChanges, 'eth_getFilterChanges')
add_method_with_lock(testrpc.eth_getFilterLogs, 'eth_getFilterLogs')
add_method_with_lock(testrpc.eth_uninstallFilter, 'eth_uninstallFilter')
add_method_with_lock(testrpc.web3_sha3, 'web3_sha3')
add_method_with_lock(testrpc.web3_clientVersion, 'web3_clientVersion')
add_method_with_lock(testrpc.evm_reset, 'evm_reset')
add_method_with_lock(testrpc.evm_snapshot, 'evm_snapshot')
add_method_with_lock(testrpc.evm_revert, 'evm_revert')


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data,
        dispatcher,
    )
    response = Response(
        response.json,
        headers=RESPONSE_HEADERS,
        mimetype='application/json',
    )
    return response