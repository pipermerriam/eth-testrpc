import pytest

from gevent import monkey
monkey.patch_socket()
import gevent
from gevent import socket
from gevent.pywsgi import (
    WSGIServer,
)

import json
import requests
import textwrap

from ethereum.utils import sha3

from eth_tester_client.utils import (
    encode_number,
    encode_hex,
    encode_data,
    strip_0x,
    force_bytes,
)


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="session")
def accounts():
    from ethereum import tester
    from eth_tester_client.utils import normalize_address
    return [normalize_address(acct) for acct in tester.accounts]
    #  return [b"0x" + encode_hex(acct) for acct in tester.accounts]


@pytest.fixture(scope="session")
def hex_accounts(accounts):
    from eth_tester_client.utils import (
        encode_address,
        force_text,
    )
    return [force_text(encode_address(acct)) for acct in accounts]


@pytest.yield_fixture()
def rpc_server():
    from testrpc.server import application
    from testrpc.testrpc import full_reset

    full_reset()

    port = get_open_port()

    server = WSGIServer(
        ('127.0.0.1', port),
        application,
    )
    gevent.spawn(server.serve_forever)

    yield server

    server.stop()


nonce = 0


@pytest.fixture()
def rpc_client(rpc_server):
    from eth_tester_client.utils import force_obj_to_text

    host, port = rpc_server.address
    endpoint = "http://{host}:{port}".format(host=host, port=port)

    def make_request(method, params=None, raise_on_error=True):
        global nonce
        nonce += 1  # NOQA
        payload = {
            "id": nonce,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
        }
        payload_data = json.dumps(force_obj_to_text(payload, True))
        response = requests.post(endpoint, data=payload_data)

        if raise_on_error:
            assert response.status_code == 200

            result = response.json()

            if 'error' in result:
                raise AssertionError(result['error'])

            assert set(result.keys()) == {"id", "jsonrpc", "result"}
        return response.json()['result']

    make_request.server = rpc_server

    return make_request


@pytest.fixture
def client():
    from eth_tester_client import EthTesterClient
    return EthTesterClient()


CONTRACT_EMITTER_SOURCE = textwrap.dedent(("""
contract Emitter {
    event LogAnonymous() anonymous;
    event LogNoArguments();
    event LogSingleArg(uint arg0);
    event LogDoubleArg(uint arg0, uint arg1);
    event LogTripleArg(uint arg0, uint arg1, uint arg2);
    event LogQuadrupleArg(uint arg0, uint arg1, uint arg2, uint arg3);

    // Indexed
    event LogSingleAnonymous(uint indexed arg0) anonymous;
    event LogSingleWithIndex(uint indexed arg0);
    event LogDoubleAnonymous(uint arg0, uint indexed arg1) anonymous;
    event LogDoubleWithIndex(uint arg0, uint indexed arg1);
    event LogTripleWithIndex(uint arg0, uint indexed arg1, uint indexed arg2);
    event LogQuadrupleWithIndex(uint arg0, uint arg1, uint indexed arg2, uint indexed arg3);

    // Bytes and String
    event LogBytes(bytes v);
    event LogString(string v);

    enum WhichEvent {
        LogAnonymous,
        LogNoArguments,
        LogSingleArg,
        LogDoubleArg,
        LogTripleArg,
        LogQuadrupleArg,
        LogSingleAnonymous,
        LogSingleWithIndex,
        LogDoubleAnonymous,
        LogDoubleWithIndex,
        LogTripleWithIndex,
        LogQuadrupleWithIndex
    }

    function logBytes(bytes v) {
        LogBytes(v);
    }

    function logString(string v) {
        LogString(v);
    }

    function logNoArgs(WhichEvent which) public {
        if (which == WhichEvent.LogNoArguments) LogNoArguments();
        else if (which == WhichEvent.LogAnonymous) LogAnonymous();
        else throw;
    }

    function logSingle(WhichEvent which, uint arg0) public {
        if (which == WhichEvent.LogSingleArg) LogSingleArg(arg0);
        else if (which == WhichEvent.LogSingleWithIndex) LogSingleWithIndex(arg0);
        else if (which == WhichEvent.LogSingleAnonymous) LogSingleAnonymous(arg0);
        else throw;
    }

    function logDouble(WhichEvent which, uint arg0, uint arg1) public {
        if (which == WhichEvent.LogDoubleArg) LogDoubleArg(arg0, arg1);
        else if (which == WhichEvent.LogDoubleWithIndex) LogDoubleWithIndex(arg0, arg1);
        else if (which == WhichEvent.LogDoubleAnonymous) LogDoubleAnonymous(arg0, arg1);
        else throw;
    }

    function logTriple(WhichEvent which, uint arg0, uint arg1, uint arg2) public {
        if (which == WhichEvent.LogTripleArg) LogTripleArg(arg0, arg1, arg2);
        else if (which == WhichEvent.LogTripleWithIndex) LogTripleWithIndex(arg0, arg1, arg2);
        else throw;
    }

    function logQuadruple(WhichEvent which, uint arg0, uint arg1, uint arg2, uint arg3) public {
        if (which == WhichEvent.LogQuadrupleArg) LogQuadrupleArg(arg0, arg1, arg2, arg3);
        else if (which == WhichEvent.LogQuadrupleWithIndex) LogQuadrupleWithIndex(arg0, arg1, arg2, arg3);
        else throw;
    }
}
"""))

CONTRACT_EMITTER_CODE = "0x60606040526104ae806100126000396000f3606060405236156100615760e060020a60003504630bb563d6811461006357806317c0c1801461013657806320f0256e1461017057806390b41d8b146101ca5780639c37705314610215578063aa6fd82214610267578063e17bf956146102a9575b005b60206004803580820135601f810184900490930260809081016040526060848152610061946024939192918401918190838280828437509496505050505050507fa95e6e2a182411e7a6f9ed114a85c3761d87f9b8f453d842c71235aa64fff99f8160405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156101255780820380516001836020036101000a031916815260200191505b509250505060405180910390a15b50565b610061600435600181141561037a577f1e86022f78f8d04f8e3dfd13a2bdb280403e6632877c0dbee5e4eeb259908a5c60006060a1610133565b6100616004356024356044356064356084356005851415610392576060848152608084815260a084905260c08390527ff039d147f23fe975a4254bdf6b1502b8c79132ae1833986b7ccef2638e73fdf991a15b5050505050565b61006160043560243560443560038314156103d457606082815260808290527fdf0cb1dea99afceb3ea698d62e705b736f1345a7eee9eb07e63d1f8f556c1bc590604090a15b505050565b6100616004356024356044356064356004841415610428576060838152608083905260a08290527f4a25b279c7c585f25eda9788ac9420ebadae78ca6b206a0e6ab488fd81f550629080a15b50505050565b61006160043560243560028214156104655760608181527f56d2ef3c5228bf5d88573621e325a4672ab50e033749a601e4f4a5e1dce905d490602090a15b5050565b60206004803580820135601f810184900490930260809081016040526060848152610061946024939192918401918190838280828437509496505050505050507f532fd6ea96cfb78bb46e09279a26828b8b493de1a2b8b1ee1face527978a15a58160405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156101255780820380516001836020036101000a03191681526020019150509250505060405180910390a150565b600081141561038d5760006060a0610133565b610002565b600b85141561038d5760608481526080849052819083907fa30ece802b64cd2b7e57dabf4010aabf5df26d1556977affb07b98a77ad955b590604090a36101c3565b600983141561040f57606082815281907f057bc32826fbe161da1c110afcdcae7c109a8b69149f727fc37a603c60ef94ca90602090a2610210565b600883141561038d5760608281528190602090a1610210565b600a84141561038d576060838152819083907ff16c999b533366ca5138d78e85da51611089cd05749f098d6c225d4cd42ee6ec90602090a3610261565b600782141561049a57807ff70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb1560006060a26102a5565b600682141561038d578060006060a16102a556"

CONTRACT_EMITTER_RUNTIME = "0x606060405236156100615760e060020a60003504630bb563d6811461006357806317c0c1801461013657806320f0256e1461017057806390b41d8b146101ca5780639c37705314610215578063aa6fd82214610267578063e17bf956146102a9575b005b60206004803580820135601f810184900490930260809081016040526060848152610061946024939192918401918190838280828437509496505050505050507fa95e6e2a182411e7a6f9ed114a85c3761d87f9b8f453d842c71235aa64fff99f8160405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156101255780820380516001836020036101000a031916815260200191505b509250505060405180910390a15b50565b610061600435600181141561037a577f1e86022f78f8d04f8e3dfd13a2bdb280403e6632877c0dbee5e4eeb259908a5c60006060a1610133565b6100616004356024356044356064356084356005851415610392576060848152608084815260a084905260c08390527ff039d147f23fe975a4254bdf6b1502b8c79132ae1833986b7ccef2638e73fdf991a15b5050505050565b61006160043560243560443560038314156103d457606082815260808290527fdf0cb1dea99afceb3ea698d62e705b736f1345a7eee9eb07e63d1f8f556c1bc590604090a15b505050565b6100616004356024356044356064356004841415610428576060838152608083905260a08290527f4a25b279c7c585f25eda9788ac9420ebadae78ca6b206a0e6ab488fd81f550629080a15b50505050565b61006160043560243560028214156104655760608181527f56d2ef3c5228bf5d88573621e325a4672ab50e033749a601e4f4a5e1dce905d490602090a15b5050565b60206004803580820135601f810184900490930260809081016040526060848152610061946024939192918401918190838280828437509496505050505050507f532fd6ea96cfb78bb46e09279a26828b8b493de1a2b8b1ee1face527978a15a58160405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156101255780820380516001836020036101000a03191681526020019150509250505060405180910390a150565b600081141561038d5760006060a0610133565b610002565b600b85141561038d5760608481526080849052819083907fa30ece802b64cd2b7e57dabf4010aabf5df26d1556977affb07b98a77ad955b590604090a36101c3565b600983141561040f57606082815281907f057bc32826fbe161da1c110afcdcae7c109a8b69149f727fc37a603c60ef94ca90602090a2610210565b600883141561038d5760608281528190602090a1610210565b600a84141561038d576060838152819083907ff16c999b533366ca5138d78e85da51611089cd05749f098d6c225d4cd42ee6ec90602090a3610261565b600782141561049a57807ff70fe689e290d8ce2b2a388ac28db36fbb0e16a6d89c6804c461f65a1b40bb1560006060a26102a5565b600682141561038d578060006060a16102a556"

CONTRACT_EMITTER_ABI = json.loads('[{"constant":false,"inputs":[{"name":"v","type":"string"}],"name":"logString","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"}],"name":"logNoArgs","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"},{"name":"arg2","type":"uint256"},{"name":"arg3","type":"uint256"}],"name":"logQuadruple","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"}],"name":"logDouble","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"},{"name":"arg1","type":"uint256"},{"name":"arg2","type":"uint256"}],"name":"logTriple","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"which","type":"uint8"},{"name":"arg0","type":"uint256"}],"name":"logSingle","outputs":[],"type":"function"},{"constant":false,"inputs":[{"name":"v","type":"bytes"}],"name":"logBytes","outputs":[],"type":"function"},{"anonymous":true,"inputs":[],"name":"LogAnonymous","type":"event"},{"anonymous":false,"inputs":[],"name":"LogNoArguments","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"}],"name":"LogSingleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"}],"name":"LogDoubleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":false,"name":"arg2","type":"uint256"}],"name":"LogTripleArg","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":false,"name":"arg2","type":"uint256"},{"indexed":false,"name":"arg3","type":"uint256"}],"name":"LogQuadrupleArg","type":"event"},{"anonymous":true,"inputs":[{"indexed":true,"name":"arg0","type":"uint256"}],"name":"LogSingleAnonymous","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"arg0","type":"uint256"}],"name":"LogSingleWithIndex","type":"event"},{"anonymous":true,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":true,"name":"arg1","type":"uint256"}],"name":"LogDoubleAnonymous","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":true,"name":"arg1","type":"uint256"}],"name":"LogDoubleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":true,"name":"arg1","type":"uint256"},{"indexed":true,"name":"arg2","type":"uint256"}],"name":"LogTripleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"arg0","type":"uint256"},{"indexed":false,"name":"arg1","type":"uint256"},{"indexed":true,"name":"arg2","type":"uint256"},{"indexed":true,"name":"arg3","type":"uint256"}],"name":"LogQuadrupleWithIndex","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"v","type":"bytes"}],"name":"LogBytes","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"v","type":"string"}],"name":"LogString","type":"event"}]')


@pytest.fixture()
def EMITTER_SOURCE():
    return CONTRACT_EMITTER_SOURCE


@pytest.fixture()
def EMITTER_CODE():
    return CONTRACT_EMITTER_CODE


@pytest.fixture()
def EMITTER_RUNTIME():
    return CONTRACT_EMITTER_RUNTIME


@pytest.fixture()
def EMITTER_ABI():
    return CONTRACT_EMITTER_ABI


@pytest.fixture()
def emitter_contract_address(client, accounts, EMITTER_CODE):
    txn_hash = client.send_transaction(
        _from=accounts[0],
        data=EMITTER_CODE,
    )
    txn_receipt = client.get_transaction_receipt(txn_hash)
    contract_address = txn_receipt['contractAddress']
    assert contract_address

    return contract_address


@pytest.fixture()
def call_emitter_contract(client, accounts, emitter_contract_address):
    def _call_emitter_contract(method_signature, arguments=None):
        if arguments is None:
            arguments = []
        function_sig = encode_data(sha3(method_signature)[:4])
        data = function_sig + b''.join((strip_0x(encode_number(arg, 32)) for arg in arguments))
        assert len(data) == 2 + 8 + 64 * len(arguments)

        txn_hash = client.send_transaction(
            _from=accounts[0],
            to=emitter_contract_address,
            data=data,
            gas=200000,
        )
        return txn_hash
    return _call_emitter_contract


class _Events(object):
    LogAnonymous = 0
    LogNoArguments = 1
    LogSingleArg = 2
    LogDoubleArg = 3
    LogTripleArg = 4
    LogQuadrupleArg = 5
    LogSingleAnonymous = 6
    LogSingleWithIndex = 7
    LogDoubleAnonymous = 8
    LogDoubleWithIndex = 9
    LogTripleWithIndex = 10
    LogQuadrupleWithIndex = 11


@pytest.fixture()
def Events():
    return _Events


def event_topic(event_signature):
    return encode_data(sha3(force_bytes(event_signature)))


class _LogTopics(object):
    LogAnonymous = event_topic("LogAnonymous()")
    LogNoArguments = event_topic("LogNoArguments()")
    LogSingleArg = event_topic("LogSingleArg(uint256)")
    LogSingleAnonymous = event_topic("LogSingleAnonymous(uint256)")
    LogSingleWithIndex = event_topic("LogSingleWithIndex(uint256)")
    LogDoubleArg = event_topic("LogDoubleArg(uint256,uint256)")
    LogDoubleAnonymous = event_topic("LogDoubleAnonymous(uint256,uint256)")
    LogDoubleWithIndex = event_topic("LogDoubleWithIndex(uint256,uint256)")
    LogTripleArg = event_topic("LogTripleArg(uint256,uint256,uint256)")
    LogTripleWithIndex = event_topic("LogTripleWithIndex(uint256,uint256,uint256)")
    LogQuadrupleArg = event_topic("LogQuadrupleArg(uint256,uint256,uint256,uint256)")
    LogQuadrupleWithIndex = event_topic("LogQuadrupleWithIndex(uint256,uint256,uint256,uint256)")
    LogBytes = event_topic("LogBytes(bytes)")
    LogString = event_topic("LogString(string)")


@pytest.fixture()
def LogTopics():
    return _LogTopics


class _LogFunctions(object):
    logNoArgs = "logNoArgs(uint8)"
    logSingle = "logSingle(uint8,uint256)"
    logDouble = "logDouble(uint8,uint256,uint256)"
    logTriple = "logTriple(uint8,uint256,uint256,uint256)"
    logQuadruple = "logQuadruple(uint8,uint256,uint256,uint256,uint256)"


@pytest.fixture
def LogFunctions():
    return _LogFunctions
