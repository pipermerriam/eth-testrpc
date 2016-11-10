import pytest

from testrpc.client.filters import check_if_topics_match


@pytest.mark.parametrize(
    'filter_topics,log_topics,expected',
    (
        ([], [], True),
        ([], ['topic_a'], True),
        ([], ['topic_a', 'topic_b'], True),
        ([None], [], False),
        ([None], ['topic_a'], True),
        ([None], ['topic_a', 'topic_b'], True),
        (['topic_a'], [], False),
        (['topic_a'], ['topic_a'], True),
        (['topic_a'], ['topic_a', 'topic_b'], True),
        ([None, 'topic_b'], [], False),
        ([None, 'topic_b'], ['topic_a'], False),
        ([None, 'topic_b'], ['topic_a', 'topic_b'], True),
        (['topic_a', 'topic_b'], [], False),
        (['topic_a', 'topic_b'], ['topic_a'], False),
        (['topic_a', 'topic_b'], ['topic_a', 'topic_b'], True),
        ([['a', 'b'], ['b', 'a']], [], False),
        ([['a', 'b'], ['b', 'a']], ['a'], False),
        ([['a', 'b'], ['b', 'a']], ['b'], False),
        ([['a', 'b'], ['b', 'a']], ['b', 'a'], True),
        ([['a', 'b'], ['b', 'a']], ['b', 'a', 'c'], True),
        ([['a', 'b'], ['b', 'a']], ['a', 'b'], True),
        ([['a', 'b'], ['b', 'a']], ['a', 'b', 'c'], True),
    ),
)
def test_matching(filter_topics, log_topics, expected):
    actual = check_if_topics_match(filter_topics, log_topics)
    assert actual is expected
