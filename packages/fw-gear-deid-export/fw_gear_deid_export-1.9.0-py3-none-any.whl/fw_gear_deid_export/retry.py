import functools
import logging

log = logging.getLogger(__name__)


class RetryException(Exception):
    u_str = "Exception ({}) raised after {} tries."

    def __init__(self, exp, max_retry):
        self.exp = exp
        self.max_retry = max_retry

    def __unicode__(self):
        return self.u_str.format(self.exp, self.max_retry)

    def __str__(self):
        return self.__unicode__()


def retry(max_retry=5):
    """
    Args:
        func: The function that needs to be retry
        max_retry (int): Maximum retry of `func` function, default is `5`

    Returns:
        func: the function to be retry

    Raises:
        RetryException: if retries exceeded than max_retry
    """

    def decorator_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            caught_exception = None
            for i in range(max_retry):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    log.debug(
                        f"Failed to call {func.__name__}, in retry({i + 1}/{max_retry})"
                    )
                    caught_exception = ex

            raise caught_exception

        return wrapper

    return decorator_wrapper


"""@retry(max_retry=2)
def failing_function():
    raise Exception("Planned Failure")

@retry(max_retry=2)
def working_function():
    return "It's Working!!!"

try:
    print(working_function())
except Exception as e:
    print("This should never happened")

try:
    print(failing_function())
except Exception as e:
    print("It Failed", e)
"""
