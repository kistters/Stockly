import logging
import uuid
from logging import Formatter, makeLogRecord

DEFAULT_RECORD_ATTRS = set(dir(makeLogRecord({})))


class ExtraFormatter(Formatter):
    def format(self, record):
        these_attrs = set(dir(record))
        extra_attrs = these_attrs - DEFAULT_RECORD_ATTRS
        record.extra = {a: getattr(record, a) for a in extra_attrs}
        record.msg += f" :: {record.extra}"
        return super().format(record)


class CorrelationIdFilter(logging.Filter):
    """
    This filter adds a correlation ID to each log record.
    """

    def filter(self, record):
        if not hasattr(record, 'correlation_id'):
            record.correlation_id = str(uuid.uuid4())
        return True
