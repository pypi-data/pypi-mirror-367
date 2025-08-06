"""
Auto-instrumentation for DTA Observability.
"""

import importlib
import logging
from typing import Any, Dict, List, Optional

from opentelemetry.metrics import Meter
from opentelemetry.sdk.resources import Resource

from dta_observability.instrumentation._create_instrumentors import (
    create_httpx_instrumentor,
    create_requests_instrumentor,
)
from dta_observability.instrumentation.detector import InstrumentationMap, PackageDetector
from dta_observability.instrumentation.registry import instrumentation_registry
from dta_observability.instrumentation.utils import handle_instrumentation_error
from dta_observability.logging.logger import get_logger


class AutoInstrumentor:
    """
    Manages automatic instrumentation of libraries.
    """

    def __init__(
        self,
        excluded_libraries: Optional[List[str]] = None,
        log_level: Optional[int] = None,
        logs_exporter_type: Optional[str] = None,
        logger: logging.Logger = get_logger("dta_observability.instrumentation"),
    ):
        """
        Initialize the auto-instrumentor.

        Args:
            excluded_libraries: List of library names to exclude from instrumentation
            log_level: The log level to use for instrumentation
            logs_exporter_type: Optional logs exporter type to use
        """
        self.log_level = log_level
        self.logs_exporter_type = logs_exporter_type
        self.excluded_libraries = set(excluded_libraries or [])
        self.instrumented_libraries: List[str] = []
        self.logger = logger


def _instrument_library(instrumentor: AutoInstrumentor, library_name: str) -> bool:
    """
    Instrument a specific library by name.

    Args:
        instrumentor: The AutoInstrumentor instance
        library_name: The name of the library to instrument

    Returns:
        True if instrumentation was successful, False otherwise
    """

    if instrumentation_registry.is_globally_instrumented(library_name):
        instrumentor.logger.debug(f"Library {library_name} already globally instrumented, skipping")
        if library_name not in instrumentor.instrumented_libraries:
            instrumentor.instrumented_libraries.append(library_name)
        return True

    module_path = InstrumentationMap.get_module_path(library_name)
    if not module_path or not (
        PackageDetector.is_available(library_name) and PackageDetector.is_available(module_path)
    ):
        instrumentor.logger.debug(f"Library {library_name} or its instrumentation is not available, skipping")
        return False

    try:
        otel_instrumentor = _create_otel_instrumentor(library_name)
        if not otel_instrumentor:
            return False

        kwargs: Dict[str, Any] = {}

        if instrumentor.log_level is not None:
            kwargs["log_level"] = instrumentor.log_level

        try:
            otel_instrumentor.instrument(**kwargs)
            instrumentation_registry.set_globally_instrumented(library_name)
            instrumentor.instrumented_libraries.append(library_name)
            return True
        except Exception as e:
            if "already instrumented" in str(e).lower():
                instrumentation_registry.set_globally_instrumented(library_name)
                instrumentor.instrumented_libraries.append(library_name)
                instrumentor.logger.debug(f"Library {library_name} was already instrumented")
                return True
            raise

    except Exception as e:
        handle_instrumentation_error(instrumentor.logger, library_name, e, "auto-instrumentation")
        return False


def _create_otel_instrumentor(library_name: str) -> Optional[Any]:
    """
    Create an OpenTelemetry instrumentor instance dynamically.

    Args:
        library_name: The name of the library to create an instrumentor for

    Returns:
        An instrumentor instance or None if creation failed
    """
    try:

        module_path = InstrumentationMap.get_module_path(library_name)
        if not module_path:
            return None

        module = importlib.import_module(module_path)
        class_name = InstrumentationMap.get_instrumentor_class_name(library_name)
        return getattr(module, class_name)()
    except (ImportError, AttributeError):
        return None


def configure_instrumentation(
    logger: logging.Logger,
    excluded_instrumentations: Optional[List[str]] = None,
    flask_app: Optional[Any] = None,
    fastapi_app: Optional[Any] = None,
    celery_app: Optional[Any] = None,
    log_level: Optional[int] = None,
    meter: Optional[Meter] = None,
    safe_logging: bool = True,
    enable_logging_instrumentation: Optional[bool] = True,
    resource_attributes: Optional[Resource] = None,
    logs_exporter_type: Optional[str] = None,
) -> None:
    """
    Configure auto-instrumentation for common libraries.

    Args:
        excluded_instrumentations: List of instrumentation names to exclude.
        flask_app: Optional Flask application instance to instrument directly.
        fastapi_app: Optional FastAPI application instance to instrument directly.
        celery_app: Optional Celery application instance to instrument directly.
        log_level: The log level to use for instrumentation.
        safe_logging: Whether to enable safe logging with complex data type handling.
        enable_logging_instrumentation: Whether to enable logging instrumentation.
        logs_exporter_type: Optional logs exporter type to use.
    """
    excluded_instrumentations = excluded_instrumentations or []

    if fastapi_app:
        if not instrumentation_registry.is_globally_instrumented("fastapi"):
            try:
                from dta_observability.instrumentation.instrumentors.fastapi import FastAPIInstrumentor

                result = FastAPIInstrumentor(
                    log_level=log_level,
                    logs_exporter_type=logs_exporter_type,
                ).instrument(fastapi_app)

                if result:
                    instrumentation_registry.set_globally_instrumented("fastapi")
                    logger.debug("FastAPI instrumentation enabled")
            except ImportError as e:
                logger.debug(f"FastAPI instrumentation not available: {e}")

    if flask_app:
        if not instrumentation_registry.is_globally_instrumented("flask"):
            try:
                from dta_observability.instrumentation.instrumentors.flask import FlaskInstrumentor

                result = FlaskInstrumentor(
                    log_level=log_level,
                    logs_exporter_type=logs_exporter_type,
                ).instrument(flask_app)

                if result:
                    instrumentation_registry.set_globally_instrumented("flask")
                    logger.debug("Flask instrumentation enabled")
            except ImportError as e:
                logger.debug(f"Flask instrumentation not available: {e}")

    if celery_app:
        if not instrumentation_registry.is_globally_instrumented("celery"):
            try:
                from dta_observability.instrumentation.instrumentors.celery import CeleryInstrumentor

                result = CeleryInstrumentor(
                    log_level=log_level,
                    logs_exporter_type=logs_exporter_type,
                ).instrument(celery_app)

                if result:
                    instrumentation_registry.set_globally_instrumented("celery")
                    logger.debug("Celery instrumentation enabled")
            except ImportError as e:
                logger.debug(f"Celery instrumentation not available: {e}")

    if not instrumentation_registry.is_globally_instrumented("faas"):
        try:
            from dta_observability.instrumentation.instrumentors import FaasInstrumentor
            faas_instrumentor = FaasInstrumentor(
                log_level=log_level,
                resource_attributes=resource_attributes,
                meter=meter,
            )
            if faas_instrumentor.instrument():
                instrumentation_registry.set_globally_instrumented("faas")
                logger.debug("FaaS instrumentation enabled")
        except ImportError as e:
            logger.debug(f"FaaS instrumentation not available: {e}")

    if not instrumentation_registry.is_globally_instrumented("container"):
        try:
            from dta_observability.instrumentation.instrumentors import ContainerInstrumentor
            container_instrumentor = ContainerInstrumentor(
                log_level=log_level,
                resource_attributes=resource_attributes,
                meter=meter,
            )
            if container_instrumentor.instrument():
                instrumentation_registry.set_globally_instrumented("container")
                logger.debug("Container instrumentation enabled")
        except ImportError as e:
            logger.debug(f"Container instrumentation not available: {e}")

    if not instrumentation_registry.is_globally_instrumented("requests"):
        create_requests_instrumentor()
        instrumentation_registry.set_globally_instrumented("requests")
        logger.debug("Requests instrumentation enabled")

    if not instrumentation_registry.is_globally_instrumented("httpx"):
        create_httpx_instrumentor()
        instrumentation_registry.set_globally_instrumented("httpx")
        logger.debug("HTTPX instrumentation enabled")

    instrumentor = AutoInstrumentor(
        excluded_libraries=excluded_instrumentations,
        log_level=log_level,
        logs_exporter_type=logs_exporter_type,
        logger=logger,
    )

    for library_name in InstrumentationMap.LIBRARIES:
        if library_name not in instrumentor.excluded_libraries:
            _instrument_library(instrumentor, library_name)

    if instrumentor.instrumented_libraries:
        logger.debug(f"Auto-instrumented libraries: {', '.join(instrumentor.instrumented_libraries)}")
        logger.debug(
            f"Globally instrumented libraries: {', '.join(instrumentation_registry.get_globally_instrumented())}"
        )
    else:
        logger.debug("No libraries were auto-instrumented")


def is_instrumentor_available(instrumentor_name: str) -> bool:
    """Check if an instrumentor is available (i.e., its dependencies are installed).

    Args:
        instrumentor_name: Name of the instrumentor (e.g., 'fastapi', 'flask', 'celery')

    Returns:
        True if the instrumentor can be imported, False otherwise
    """
    try:
        if instrumentor_name == "fastapi":
            from dta_observability.instrumentation.instrumentors import FastAPIInstrumentor  # noqa: F401 
        elif instrumentor_name == "flask":
            from dta_observability.instrumentation.instrumentors import FlaskInstrumentor  # noqa: F401 
        elif instrumentor_name == "celery":
            from dta_observability.instrumentation.instrumentors import CeleryInstrumentor  # noqa: F401 
        else:
            return False
        return True
    except ImportError:
        return False
