"""
Functions for creating instrumentors with hooks.
"""

from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from dta_observability.instrumentation.utils import (
    httpx_async_request_hook,
    httpx_async_response_hook,
    httpx_request_hook,
    httpx_response_hook,
    requests_request_hook,
    requests_response_hook,
)


def create_requests_instrumentor() -> RequestsInstrumentor:
    """Create a requests instrumentor with the custom request hook.

    Returns:
        A configured RequestsInstrumentor instance
    """
    instrumentor = RequestsInstrumentor()

    instrumentor.instrument(
        request_hook=requests_request_hook,
        response_hook=requests_response_hook,
        excluded_urls="client/.*/info,healthcheck,googleapis.com,oauth2.googleapis.com",
    )
    return instrumentor


def create_httpx_instrumentor() -> HTTPXClientInstrumentor:
    """Create an HTTPX instrumentor with the custom request hooks.

    Returns:
        A configured HTTPXClientInstrumentor instance
    """
    instrumentor = HTTPXClientInstrumentor()
    instrumentor.instrument(
        request_hook=httpx_request_hook,
        response_hook=httpx_response_hook,
        async_request_hook=httpx_async_request_hook,
        async_response_hook=httpx_async_response_hook,
    )
    return instrumentor
