"""Instrumentors for specific libraries and frameworks."""

import importlib

__all__ = [
    "CeleryInstrumentor",
    "FastAPIInstrumentor",
    "FlaskInstrumentor",
    "LoggingInstrumentor",
    "FaasInstrumentor",
    "ContainerInstrumentor",
]


def __getattr__(name: str):
    """Lazy import for instrumentors to handle optional dependencies."""
    instrumentor_map = {
        "CeleryInstrumentor": ("celery", "CeleryInstrumentor requires celery to be installed"),
        "ContainerInstrumentor": ("container", "ContainerInstrumentor is not available"),
        "FaasInstrumentor": ("faas", "FaasInstrumentor is not available"),
        "FastAPIInstrumentor": ("fastapi", "FastAPIInstrumentor requires fastapi to be installed"),
        "FlaskInstrumentor": ("flask", "FlaskInstrumentor requires flask to be installed"),
        "LoggingInstrumentor": ("logging", "LoggingInstrumentor is not available"),
    }
    
    if name in instrumentor_map:
        module_name, error_message = instrumentor_map[name]
        try:
            module = importlib.import_module(f"dta_observability.instrumentation.instrumentors.{module_name}")
            return getattr(module, name)
        except (ImportError, AttributeError):
            raise ImportError(error_message)
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
