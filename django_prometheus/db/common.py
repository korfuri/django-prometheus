import sys


def get_current_exception_type():
    """Returns the name of the type of the current exception."""
    ex_type = sys.exc_info()[0]
    if ex_type is None:
        return '<no exception>'
    return ex_type.__name__
