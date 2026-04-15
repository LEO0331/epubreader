from __future__ import annotations

import logging

from packages.core.logging.request_context import request_id_ctx_var


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get() or "-"
        return True


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())

    if not root.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

    has_filter = any(isinstance(filter_obj, RequestIdFilter) for filter_obj in root.filters)
    if not has_filter:
        root.addFilter(RequestIdFilter())
