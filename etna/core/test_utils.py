import logging


def prevent_request_warnings(original_function):
    """
    If we need to test for 503s this decorator can prevent the
    request class from throwing warnings.
    """

    def new_function(*args, **kwargs):
        # raise logging level to CRITICAL
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function
