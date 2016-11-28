import os
import signal

import gevent

from click.testing import CliRunner

from testrpc.cli import runserver
from testrpc.rpc import RPCMethods


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def test_main_module_for_cli_server_running():
    runner = CliRunner()

    port = get_open_port()

    pid = os.getpid()

    def kill_it():
        gevent.sleep(2)
        os.kill(pid, signal.SIGINT)

    gevent.spawn(kill_it)

    result = runner.invoke(runserver, ['--port', str(port)])
    assert result.exit_code == 0

    assert str(port) in result.output
    assert RPCMethods().web3_clientVersion() in result.output
