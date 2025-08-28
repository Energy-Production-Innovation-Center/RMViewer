from rmviewer.logger.custom_logger import Logger


def log_exceptions(message: str):
    """
    Decorator to log exceptions.

    :param message: Error message
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:
                Logger().log_error(f"{message}: {ex}")

        return wrapper

    return decorator
