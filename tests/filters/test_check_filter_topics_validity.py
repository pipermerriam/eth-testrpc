import pytest

from testrpc.client.filters import *
from testrpc.client.filters import (
    check_filter_topics_validity,
)


@pytest.mark.parametrize(
    'filter_topics,expected',
    (
        # valid
        ([], True),
        (['A'], True),
        ([None, 'A'], True),
        (['A', 'B'], True),
        ([['A', 'B'], ['B', 'A']], True),
        # invalid
        (None, False),
        (1, False),
        ([1], False),
        (['A', 1], False),  # integer type
        ([['A', 2], ['B', 'A']], False),
        ([[['A', 'B'], ['B', 'A']], ['A', 'A']], False),  # 3 deep nesting
    ),
)
def test_check_filter_topics_validity(filter_topics, expected):
    actual = check_filter_topics_validity(filter_topics)
    assert actual is expected
