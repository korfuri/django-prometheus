import time

# TODO(korfuri): if python>3.3, use perf_counter() or monotonic().


def Time():
    """Returns some representation of the current time.

    This wrapper is meant to take advantage of a higher time
    resolution when available. Thus, its return value should be
    treated as an opaque object. It can be compared to the current
    time with TimeSince().
    """
    return time.time()


def TimeSince(t):
    """Compares a value returned by Time() to the current time.

    Returns:
      the time since t, in fractional seconds.
    """
    return time.time() - t
