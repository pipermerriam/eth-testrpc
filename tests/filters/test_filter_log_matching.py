import pytest

from eth_tester_client.utils import (
    encode_number,
    encode_data,
    coerce_args_to_bytes,
)
from eth_tester_client.filters import (
    check_if_log_matches,
)




@coerce_args_to_bytes
def make_log_filter(from_block="latest", to_block="latest", addresses=None, topics=None):
    if addresses is None:
        addresses = []
    if topics is None:
        topics = []

    log_filter = {
        'from_block': from_block,
        'to_block': to_block,
        'addresses': addresses,
        'filter_topics': topics,
    }
    return log_filter


@coerce_args_to_bytes
def make_log_entry(block_number=1,
                   type=b"mined",
                   address=b"0xd3cda913deb6f67967b99d67acdfa1712c293601",
                   topics=None,
                   data=b""):
    if topics is None:
        topics = []

    log_entry = {
        "type": type,
        "logIndex": "0x0",
        "transactionIndex": "0x0",
        "transactionHash": "0xebb0f76aa6a6bb8d178bc2b54ae8fd7ca778d703bf47d135c188ca2b6d25f2e4",
        "blockHash": "0xd2f44ad2d3702136acccacb5098829585e63b5e1e264b0e54c4d5af2edb87368",
        "blockNumber": encode_number(block_number),
        "address": address,
        "data": encode_data(data),
        "topics": topics,
    }
    return log_entry


@pytest.mark.parametrize(
    'log_filter,log_entry,expected',
    (
        (make_log_filter(), make_log_entry(), True),
        (make_log_filter(), make_log_entry(topics=['a']), True),
    ),
)
def test_check_if_filter_matches_log(log_filter, log_entry, expected):
    actual = check_if_log_matches(log_entry, **log_filter)
    assert actual is expected
