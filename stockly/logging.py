import logging
import time
from datetime import datetime
from functools import wraps

DEFAULT_RECORD_ATTRS = set(dir(logging.makeLogRecord({})))


class ExtraFormatter(logging.Formatter):
    def format(self, record):
        these_attrs = set(dir(record))
        extra_attrs = these_attrs - DEFAULT_RECORD_ATTRS
        record.extra = {a: getattr(record, a) for a in extra_attrs}
        record.msg += f" :: {record.extra}"
        return super().format(record)


def log_duration(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"{func.__name__}.duration", extra={
                "duration_ms": f"{duration * 1000:.3f}",
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
            })
            return result

        return wrapper

    return decorator
