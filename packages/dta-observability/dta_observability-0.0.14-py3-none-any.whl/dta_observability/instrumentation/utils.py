"""
Instrumentation utilities for DTA Observability.
"""

import logging
from typing import Any, Optional

from opentelemetry.trace import Status, StatusCode


def handle_instrumentation_error(
    logger: logging.Logger, library_name: str, error: Exception, context: str = "instrumentation"
) -> None:
    """
    Handle instrumentation errors consistently.

    Args:
        logger: Logger to use for recording errors
        library_name: The name of the library that failed to instrument
        error: The exception that was raised
        context: Context where the error occurred (default: "instrumentation")
    """
    logger.warning("Failed to instrument %s (%s): %s - %s", library_name, context, error.__class__.__name__, str(error))
    logger.debug("Instrumentation error details", exc_info=error)


def configure_framework_logging(log_level: Optional[int] = None) -> None:
    """
    Configure logging for web servers like gunicorn and werkzeug.

    Args:
        log_level: Logging level to apply
    """

    if log_level == logging.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    all_loggers = [
        logging.getLogger("werkzeug"),
        logging.getLogger("werkzeug.access"),
        logging.getLogger("werkzeug.error"),
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("fastapi"),
        logging.getLogger("celery"),
        logging.getLogger("celery.app"),
        logging.getLogger("celery.app.trace"),
        logging.getLogger("celery.app.trace.worker"),
        logging.getLogger("celery.app.trace.worker.pool"),
        logging.getLogger("fastapi.access"),
        logging.getLogger("fastapi.error"),
        logging.getLogger("fastapi.routing"),
        logging.getLogger("gunicorn"),
        logging.getLogger("gunicorn.error"),
        logging.getLogger("gunicorn.access"),
        logging.getLogger("flask"),
        logging.getLogger("flask.app"),
        logging.getLogger("flask.error"),
        logging.getLogger("flask.access"),
    ]

    for logger in all_loggers:
        logger.setLevel(log_level)
        logger.disabled = True
        logger.propagate = False


def check_instrumentation_status(object_to_check: Any, library_name: str, attr_name: str) -> bool:
    """
    Check if an object has already been instrumented.

    Args:
        object_to_check: The object to check for instrumentation status
        library_name: The name of the library being instrumented (for logging)
        attr_name: The attribute name that marks the object as instrumented

    Returns:
        True if the object is already instrumented, False otherwise
    """
    return hasattr(object_to_check, attr_name) and bool(getattr(object_to_check, attr_name))


def httpx_request_hook(span, request):
    method = str(request.method)
    url = str(request.url)
    span.update_name(f"{method} {url} (OUTGOING)")


async def httpx_async_request_hook(span, request):
    method = str(request.method)
    url = str(request.url)
    span.update_name(f"{method} {url} (OUTGOING)")


def httpx_response_hook(span, request, response):
    status_code = response[0]
    method = str(request.method)
    url = str(request.url)
    span.update_name(f"{method} {url} (OUTGOING) - {status_code}")

    if status_code >= 400:
        span.set_status(Status(StatusCode.ERROR))
    else:
        span.set_status(Status(StatusCode.OK))


async def httpx_async_response_hook(span, request, response):
    status_code = response[0]
    method = str(request.method)
    url = str(request.url)
    span.update_name(f"{method} {url} (OUTGOING) - {status_code}")

    if status_code >= 400:
        span.set_status(Status(StatusCode.ERROR))
    else:
        span.set_status(Status(StatusCode.OK))


def requests_request_hook(span, request):
    method = str(request.method)
    url = str(request.url)
    span.update_name(f"{method} {url} (OUTGOING)")


def requests_response_hook(span, request_obj, response):
    method = str(request_obj.method)
    url = str(request_obj.url)
    span.update_name(f"{method} {url} (OUTGOING) - {response.status_code}")

    if response.status_code >= 400:
        span.set_status(Status(StatusCode.ERROR))
    else:
        span.set_status(Status(StatusCode.OK))
