"""
Logging instrumentation for DTA Observability.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry._logs.severity import std_to_otel
from opentelemetry.instrumentation.logging import LoggingInstrumentor as OTelLoggingInstrumentor
from opentelemetry.sdk._logs import LoggingHandler, LogRecord
from opentelemetry.sdk.trace import Span
from opentelemetry.semconv.trace import SpanAttributes
from pythonjsonlogger.json import JsonFormatter as PythonJsonFormatter


class LogFieldMap:
    """Constants for log field mapping."""

    TIMESTAMP = "timestamp"
    SEVERITY = "severity"
    LOGGER = "logger"
    MESSAGE = "message"

    TRACE_ID = "logging.googleapis.com/trace"
    SPAN_ID = "logging.googleapis.com/spanId"
    TRACE_SAMPLED = "logging.googleapis.com/trace_sampled"

    OTEL_TRACE_ID = "otelTraceID"
    OTEL_SPAN_ID = "otelSpanID"
    OTEL_TRACE_SAMPLED = "otelTraceSampled"

    ERROR_TYPE = "error_type"
    ERROR_MESSAGE = "error_message"


class JsonFormatter(PythonJsonFormatter):
    """JSON formatter with RFC 3339 timestamps and safe handling of complex data types."""

    def __init__(self, *args, safe_logging: bool = True, **kwargs):
        """Initialize the JSON formatter."""
        super().__init__(*args, **kwargs)
        self.safe_logging = safe_logging

    def _handle_complex_value(self, value: Any) -> Any:
        """Safely convert complex types to serializable values."""

        if value is None or isinstance(value, (str, int, float, bool)):
            return "" if value is None else value

        if isinstance(value, (list, tuple)):
            return [self._handle_complex_value(item) for item in value] if value else []

        if isinstance(value, dict):
            return {str(k): self._handle_complex_value(v) for k, v in value.items()} if value else {}

        try:
            return json.dumps(value)
        except Exception:
            return str(value)

    def format(self, record: logging.LogRecord) -> str:
        """Format the record with safe handling of complex types."""
        if not self.safe_logging:
            return super().format(record)

        record_copy = logging.LogRecord(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=record.msg,
            args=record.args,
            exc_info=record.exc_info,
        )

        for attr, value in record.__dict__.items():
            if attr not in record_copy.__dict__:
                setattr(record_copy, attr, value)

        try:

            if hasattr(record_copy, "extra") and isinstance(record_copy.extra, dict):
                record_copy.extra = {k: self._handle_complex_value(v) for k, v in record_copy.extra.items()}

            if isinstance(record_copy.args, dict):
                record_copy.args = {k: self._handle_complex_value(v) for k, v in record_copy.args.items()}
            elif isinstance(record_copy.args, tuple):
                record_copy.args = tuple(self._handle_complex_value(arg) for arg in record_copy.args)
            elif record_copy.args:
                record_copy.args = self._handle_complex_value(record_copy.args)

            if not isinstance(record_copy.msg, str):
                record_copy.msg = str(record_copy.msg)

            return super().format(record_copy)

        except Exception:

            try:
                simple_record = logging.LogRecord(
                    name=record.name,
                    level=record.levelno,
                    pathname=record.pathname,
                    lineno=record.lineno,
                    msg=str(record.msg) if record.msg is not None else "",
                    args=(),
                    exc_info=record.exc_info,
                )

                for attr in ["otelTraceID", "otelSpanID", "otelTraceSampled"]:
                    if hasattr(record, attr):
                        setattr(simple_record, attr, getattr(record, attr))

                return super().format(simple_record)
            except Exception:

                return super().format(
                    logging.LogRecord(
                        name=record.name,
                        level=record.levelno,
                        pathname=record.pathname,
                        lineno=record.lineno,
                        msg="[Logging Error: Unable to format log message]",
                        args=(),
                        exc_info=None,
                    )
                )


class LogRecordFilter(logging.Filter):
    """Filter that ensures log records have necessary attributes."""

    REQUIRED_ATTRIBUTES = {
        "otelTraceID": "",
        "otelSpanID": "",
        "otelTraceSampled": "",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Ensure log records have all required attributes and safe values.

        This filter:
        1. Adds default trace context fields if missing
        2. Ensures all extra fields are serializable
        3. Handles non-serializable types gracefully
        4. Converts dictionary attributes to JSON strings
        5. Ensures exc_info is properly formatted
        6. Preserves message formatting
        7. Properly formats trace IDs for GCP

        All logs will pass through (always returns True).
        """

        for attr, default_value in self.REQUIRED_ATTRIBUTES.items():
            if not hasattr(record, attr):
                setattr(record, attr, default_value)

        if not record.otelTraceID.startswith("projects/"):  # type: ignore
            record.otelTraceID = LoggingConfigurator.format_gcp_trace_id(record.otelTraceID)  # type: ignore

        if hasattr(record, "exc_info") and record.exc_info:
            if not isinstance(record.exc_info, tuple) or len(record.exc_info) != 3:

                try:
                    import sys

                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    if any((exc_type, exc_value, exc_traceback)):
                        record.exc_info = (exc_type, exc_value, exc_traceback)
                    else:
                        record.exc_info = None
                except Exception:
                    record.exc_info = None

        original_msg = record.msg
        original_args = record.args

        for attr_name in dir(record):

            if (
                attr_name.startswith("_")
                or callable(getattr(record, attr_name))
                or attr_name in ("exc_info", "exc_text", "stack_info", "msg", "args", "message")
            ):
                continue

            value = getattr(record, attr_name)

            if isinstance(value, dict):
                try:
                    setattr(record, attr_name, json.dumps(value))
                except Exception:
                    setattr(record, attr_name, str(value))

            elif not isinstance(value, (str, int, float, bool, bytes, type(None))):
                try:
                    if hasattr(value, "__dict__"):
                        setattr(record, attr_name, json.dumps(value.__dict__))
                    else:
                        setattr(record, attr_name, json.dumps(value))
                except Exception:
                    setattr(record, attr_name, str(value))

        if hasattr(record, "extra") and isinstance(record.extra, dict):
            safe_extra: Dict[str, Any] = {}

            for key, value in record.extra.items():

                if isinstance(value, dict):
                    try:
                        safe_extra[key] = json.dumps(value)
                    except Exception:
                        safe_extra[key] = str(value)

                elif not isinstance(value, (str, int, float, bool, bytes, type(None))):
                    try:

                        if hasattr(value, "__dict__"):
                            safe_extra[key] = json.dumps(value.__dict__)
                        else:
                            safe_extra[key] = json.dumps(value)
                    except Exception:

                        safe_extra[key] = str(value)
                else:

                    safe_extra[key] = value

            record.extra = safe_extra

        record.msg = original_msg
        record.args = original_args

        return True


class LoggingConfigurator:
    """Central configuration manager for logging."""

    _configured = False
    _lock = __import__("threading").RLock()
    _instance = None

    LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s"

    GCP_FIELD_MAPPING = {
        "levelname": LogFieldMap.SEVERITY,
        "asctime": LogFieldMap.TIMESTAMP,
        "name": LogFieldMap.LOGGER,
        LogFieldMap.OTEL_TRACE_ID: LogFieldMap.TRACE_ID,
        LogFieldMap.OTEL_SPAN_ID: LogFieldMap.SPAN_ID,
        LogFieldMap.OTEL_TRACE_SAMPLED: LogFieldMap.TRACE_SAMPLED,
    }

    @staticmethod
    def format_gcp_trace_id(trace_id: str) -> str:
        """Format trace ID for GCP Cloud Logging.

        Args:
            trace_id: Raw trace ID

        Returns:
            Formatted trace ID for GCP: 'projects/{project_id}/traces/{trace_id}'
        """
        import os

        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or "unknown"
        return f"projects/{project_id}/traces/{trace_id}"

    @classmethod
    def is_configured(cls) -> bool:
        """Check if logging has been configured."""
        with cls._lock:
            return cls._configured

    @classmethod
    def mark_configured(cls) -> None:
        """Mark logging as configured."""
        with cls._lock:
            cls._configured = True

    @classmethod
    def create_formatter(cls, safe_logging: bool = True) -> JsonFormatter:
        """Create a properly configured JSON formatter."""
        return JsonFormatter(
            cls.LOG_FORMAT,
            safe_logging=safe_logging,
            rename_fields=cls.GCP_FIELD_MAPPING,
        )

    @classmethod
    def create_handler(cls, level: int, safe_logging: bool = True, log_format: Optional[str] = None) -> logging.Handler:
        """Create a logging handler with proper configuration."""

        handler: logging.Handler

        OTelLoggingInstrumentor().instrument(
            set_logging_format=False,
            log_hook=cls.log_hook,
            log_level=level,
        )

        if log_format != "gcp":
            handler = LoggingHandler()
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(cls.create_formatter(safe_logging=safe_logging))
        handler.addFilter(LogRecordFilter())
        setattr(handler, "_dta_otel_handler", True)
        return handler

    @staticmethod
    def has_dta_handler(logger: logging.Logger) -> bool:
        """Check if a logger already has a DTA handler."""
        return any(hasattr(handler, "_dta_otel_handler") for handler in logger.handlers)

    @classmethod
    def configure_root_logger(cls, level: int, handler: logging.Handler, replace_existing: bool = False) -> None:
        """Configure the root logger."""

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        if not replace_existing and cls.has_dta_handler(root_logger):
            return

        if replace_existing or not root_logger.handlers:
            for existing_handler in root_logger.handlers[:]:
                root_logger.removeHandler(existing_handler)
            root_logger.addHandler(handler)

    @staticmethod
    def log_hook(self, span: Span, record: logging.LogRecord, formatted: str = ""):
        if span and span.is_recording():
            ctx = span.get_span_context()
            session_id, request_id = self._instance.get_highlight_context(span.context.trace_id)
            # record.created is sec but timestamp should be ns
            ts = int(record.created * 1000.0 * 1000.0 * 1000.0)
            attributes = {}
            if span.attributes is not None:
                attributes = dict(span.attributes)
            attributes[SpanAttributes.CODE_FUNCTION] = record.funcName
            attributes[SpanAttributes.CODE_NAMESPACE] = record.module
            attributes[SpanAttributes.CODE_FILEPATH] = record.pathname
            attributes[SpanAttributes.CODE_LINENO] = record.lineno
            attributes["logger"] = record.name
            attributes["highlight.trace_id"] = request_id
            attributes["highlight.session_id"] = session_id
            if isinstance(record.args, dict):
                attributes.update(record.args)
            elif isinstance(record.args, list):
                attributes["args"] = record.args
            elif record.args:
                attributes["args"] = str(record.args)

            message = formatted or record.getMessage()
            obj = json.loads(message)
            extra = obj["record"]["extra"]
            message = obj["text"]

            for key, value in extra.items():
                attributes[key] = value

            attributes = flatten_dict(attributes, sep=".")

            if record.exc_info:
                attributes["exception.detail"] = message
                return self.record_exception(record.exc_info[1], attributes=attributes)

            r = LogRecord(
                timestamp=ts,
                trace_id=ctx.trace_id,
                span_id=ctx.span_id,
                trace_flags=ctx.trace_flags,
                severity_text=record.levelname,
                severity_number=std_to_otel(record.levelno),
                body=message,
                resource=span.resource,
                attributes=attributes,
            )
            self.log.emit(r)


class DTAErrorHandler:
    """Handles exceptions with proper context."""

    def __init__(self) -> None:
        """Initialize the error handler."""
        self._logger = None

    @property
    def logger(self):
        """Lazy-load the logger to avoid circular dependencies."""
        if self._logger is None:
            self._logger = get_logger("dta_observability.error")
        return self._logger

    def handle(self, error: Exception) -> None:
        """Log an error with trace context."""
        context = self._build_error_context(error)

        import traceback

        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_traceback:
            formatted_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            self.logger.error(f"Unhandled exception: {error}\n{formatted_traceback}", extra=context)
        else:

            self.logger.error(f"Unhandled exception: {error}", extra=context)

    def _build_error_context(self, error: Exception) -> Dict[str, Any]:
        """Build error context with trace information."""

        context = {
            LogFieldMap.ERROR_TYPE: error.__class__.__name__,
            LogFieldMap.ERROR_MESSAGE: str(error),
        }

        current_span = trace.get_current_span()
        if current_span:
            span_context = current_span.get_span_context()
            if span_context:
                context.update(
                    {
                        "trace_id": hex(span_context.trace_id)[2:],
                        "span_id": hex(span_context.span_id)[2:],
                    }
                )

        return context


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger with tracing capabilities.

    This is the main entry point for getting loggers in the application.
    Loggers created through this function will have:
    - JSON formatting
    - Trace context propagation
    - Safe handling of complex data
    - Proper log levels

    Args:
        name: Logger name, typically the module name

    Returns:
        A Logger instance
    """
    logger = logging.getLogger(name)

    if not hasattr(logger, "_dta_instrumented_logger"):
        setattr(logger, "_dta_instrumented_logger", True)
        setattr(logger, "_dta_handler", DTAErrorHandler())

        from dta_observability.core.config import get_log_level

        logger.setLevel(get_log_level())

    logger.propagate = True
    return logger


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
