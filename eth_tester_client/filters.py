import functools

from .utils import (
    is_string,
    is_numeric,
    is_array,
    coerce_args_to_bytes,
)


def is_empty_array(value):
    return value == [] or value == tuple()


def is_topic_array(value):
    if not is_array(value):
        return False
    return all(is_string(item) or item is None for item in value)


def is_nested_topic_array(value):
    if not is_array(value):
        return False

    return all((is_topic_array(item) for item in value))


def check_filter_topics_validity(filter_topics):
    return any((
        is_empty_array(filter_topics),
        is_topic_array(filter_topics),
        is_nested_topic_array(filter_topics),
    ))


@coerce_args_to_bytes
def check_topic_match(filter_topic, log_topic):
    if filter_topic is None:
        return True
    return filter_topic == log_topic


@coerce_args_to_bytes
def check_if_topics_match(filter_topics, log_topics):
    if is_empty_array(filter_topics):
        return True
    elif is_topic_array(filter_topics):
        if len(filter_topics) > len(log_topics):
            return False
        return all(
            check_topic_match(filter_topic, log_topic)
            for filter_topic, log_topic
            in zip(filter_topics, log_topics)
        )
    elif is_nested_topic_array(filter_topics):
        return any(
            check_if_topics_match(sub_topics, log_topics)
            for sub_topics in filter_topics
        )
    else:
        raise ValueError("Invalid filter topics format")


@coerce_args_to_bytes
def check_if_log_matches(log_entry, from_block, to_block,
                         addresses, filter_topics):
    #
    # validate `from_block` (left bound)
    #
    if is_string(from_block):
        raise NotImplementedError("not implemented")
    elif is_numeric(from_block):
        if from_block > log_entry['blockNumber']:
            return False
    else:
        raise TypeError("Invalid `from_block`")

    #
    # validate `to_block` (left bound)
    #
    if is_string(to_block):
        raise NotImplementedError("not implemented")
    elif is_numeric(to_block):
        if to_block < log_entry['blockNumber']:
            return False
    else:
        raise TypeError("Invalid `to_block`")

    #
    # validate `addresses`
    #
    if addresses and log_entry['address'] not in addresses:
        return False

    #
    # validate `topics`
    if not check_if_topics_match(filter_topics, log_entry['topics']):
        return False

    return True


def process_block(block, from_block, to_block, addresses, filter_topics):
    log_match_fn = functools.partial(
        check_if_log_matches,
        from_block=from_block,
        to_block=to_block,
        addresses=addresses,
        filter_topics=filter_topics,
    )
    import pdb; pdb.set_trac()
    for raw_log in block.logs:
        pass
        #log_entry =
