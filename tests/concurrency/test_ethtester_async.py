import pytest

from ethereum import tester
from ethereum import utils

from testrpc.client import EthTesterClient
from testrpc import async


def test_async_requests():
    client = EthTesterClient()

    threads = []
    errors = []
    to_addr = utils.encode_hex(tester.accounts[1])

    def spam_block_number():
        for i in range(2):
            try:
                client.send_transaction(
                    to=to_addr,
                    value=1,
                )
            except Exception as e:
                errors.append(e)
                pytest.fail(''.join(e.args))

    for i in range(3):
        thread = async.spawn(spam_block_number)
        threads.append(thread)

    assert threads
    [thread.join() for thread in threads]

    assert not errors
