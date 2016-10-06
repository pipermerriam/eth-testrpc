import pytest
import gevent

from ethereum import tester
from ethereum import utils

from eth_tester_client import EthTesterClient


def test_async_requests():
    client = EthTesterClient()

    threads = []
    errors = []
    to_addr = utils.encode_hex(tester.accounts[1])

    def spam_block_number():
        for i in range(5):
            try:
                client.send_transaction(
                    to=to_addr,
                    value=1,
                )
            except Exception as e:
                errors.append(e)
                pytest.fail(''.join(e.args))

    for i in range(5):
        thread = gevent.spawn(spam_block_number)

    [thread.join() for thread in threads]

    assert not errors
