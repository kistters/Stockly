import logging

DEFAULT_RECORD_ATTRS = set(dir(logging.makeLogRecord({})))


class ExtraFormatter(logging.Formatter):
    def format(self, record):
        these_attrs = set(dir(record))
        extra_attrs = these_attrs - DEFAULT_RECORD_ATTRS
        record.extra = {a: getattr(record, a) for a in extra_attrs}
        record.msg += f" :: {record.extra}"
        return super().format(record)
