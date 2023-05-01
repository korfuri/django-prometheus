import copy

from prometheus_client import REGISTRY

METRIC_EQUALS_ERR_EXPLANATION = """
%s%s = %s, expected %s.
The values for %s are:
%s"""

METRIC_DIFF_ERR_EXPLANATION = """
%s%s changed by %f, expected %f.
Value before: %s
Value after: %s
"""

METRIC_COMPARE_ERR_EXPLANATION = """
The change in value of %s%s didn't match the predicate.
Value before: %s
Value after: %s
"""

METRIC_DIFF_ERR_NONE_EXPLANATION = """
%s%s was None after.
Value before: %s
Value after: %s
"""


"""A collection of utilities that make it easier to write test cases
that interact with metrics.
"""


def assert_metric_equal(expected_value, metric_name, registry=REGISTRY, **labels):
    """Asserts that metric_name{**labels} == expected_value."""
    value = get_metric(metric_name, registry=registry, **labels)
    assert_err = METRIC_EQUALS_ERR_EXPLANATION % (
        metric_name,
        format_labels(labels),
        value,
        expected_value,
        metric_name,
        format_vector(get_metrics_vector(metric_name)),
    )
    assert expected_value == value, assert_err


def assert_metric_diff(frozen_registry, expected_diff, metric_name, registry=REGISTRY, **labels):
    """Asserts that metric_name{**labels} changed by expected_diff between
    the frozen registry and now. A frozen registry can be obtained
    by calling save_registry, typically at the beginning of a test
    case.
    """
    saved_value = get_metric_from_frozen_registry(metric_name, frozen_registry, **labels)
    current_value = get_metric(metric_name, registry=registry, **labels)
    assert current_value is not None, METRIC_DIFF_ERR_NONE_EXPLANATION % (
        metric_name,
        format_labels(labels),
        saved_value,
        current_value,
    )
    diff = current_value - (saved_value or 0.0)
    assert_err = METRIC_DIFF_ERR_EXPLANATION % (
        metric_name,
        format_labels(labels),
        diff,
        expected_diff,
        saved_value,
        current_value,
    )
    assert expected_diff == diff, assert_err


def assert_metric_no_diff(frozen_registry, expected_diff, metric_name, registry=REGISTRY, **labels):
    """Asserts that metric_name{**labels} isn't changed by expected_diff between
    the frozen registry and now. A frozen registry can be obtained
    by calling save_registry, typically at the beginning of a test
    case.
    """
    saved_value = get_metric_from_frozen_registry(metric_name, frozen_registry, **labels)
    current_value = get_metric(metric_name, registry=registry, **labels)
    assert current_value is not None, METRIC_DIFF_ERR_NONE_EXPLANATION % (
        metric_name,
        format_labels(labels),
        saved_value,
        current_value,
    )
    diff = current_value - (saved_value or 0.0)
    assert_err = METRIC_DIFF_ERR_EXPLANATION % (
        metric_name,
        format_labels(labels),
        diff,
        expected_diff,
        saved_value,
        current_value,
    )
    assert expected_diff != diff, assert_err


def assert_metric_not_equal(expected_value, metric_name, registry=REGISTRY, **labels):
    """Asserts that metric_name{**labels} == expected_value."""
    value = get_metric(metric_name, registry=registry, **labels)
    assert_err = METRIC_EQUALS_ERR_EXPLANATION % (
        metric_name,
        format_labels(labels),
        value,
        expected_value,
        metric_name,
        format_vector(get_metrics_vector(metric_name)),
    )
    assert expected_value != value, assert_err


def assert_metric_compare(frozen_registry, predicate, metric_name, registry=REGISTRY, **labels):
    """Asserts that metric_name{**labels} changed according to a provided
    predicate function between the frozen registry and now. A
    frozen registry can be obtained by calling save_registry,
    typically at the beginning of a test case.
    """
    saved_value = get_metric_from_frozen_registry(metric_name, frozen_registry, **labels)
    current_value = get_metric(metric_name, registry=registry, **labels)
    assert current_value is not None, METRIC_DIFF_ERR_NONE_EXPLANATION % (
        metric_name,
        format_labels(labels),
        saved_value,
        current_value,
    )
    assert predicate(saved_value, current_value) is True, METRIC_COMPARE_ERR_EXPLANATION % (
        metric_name,
        format_labels(labels),
        saved_value,
        current_value,
    )


def save_registry(registry=REGISTRY):
    """Freezes a registry. This lets a user test changes to a metric
    instead of testing the absolute value. A typical use case looks like:

        registry = save_registry()
        doStuff()
        assert_metric_diff(registry, 1, 'stuff_done_total')
    """
    return copy.deepcopy(list(registry.collect()))


def get_metric(metric_name, registry=REGISTRY, **labels):
    """Gets a single metric."""
    return get_metric_from_frozen_registry(metric_name, registry.collect(), **labels)


def get_metrics_vector(metric_name, registry=REGISTRY):
    """Returns the values for all labels of a given metric.

    The result is returned as a list of (labels, value) tuples,
    where `labels` is a dict.

    This is quite a hack since it relies on the internal
    representation of the prometheus_client, and it should
    probably be provided as a function there instead.
    """
    return get_metric_vector_from_frozen_registry(metric_name, registry.collect())


def get_metric_vector_from_frozen_registry(metric_name, frozen_registry):
    """Like get_metrics_vector, but from a frozen registry."""
    output = []
    for metric in frozen_registry:
        for sample in metric.samples:
            if sample[0] == metric_name:
                output.append((sample[1], sample[2]))
    return output


def get_metric_from_frozen_registry(metric_name, frozen_registry, **labels):
    """Gets a single metric from a frozen registry."""
    for metric in frozen_registry:
        for sample in metric.samples:
            if sample[0] == metric_name and sample[1] == labels:
                return sample[2]


def format_labels(labels):
    """Format a set of labels to Prometheus representation.

    In:
      {'method': 'GET', 'port': '80'}

    Out:
      '{method="GET",port="80"}'
    """
    return "{%s}" % ",".join([f'{k}="{v}"' for k, v in labels.items()])


def format_vector(vector):
    """Formats a list of (labels, value) where labels is a dict into a
    human-readable representation.
    """
    return "\n".join([f"{format_labels(labels)} = {value}" for labels, value in vector])
