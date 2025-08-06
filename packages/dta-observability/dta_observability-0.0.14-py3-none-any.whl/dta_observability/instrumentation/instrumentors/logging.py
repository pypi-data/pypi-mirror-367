"""
Logging-specific instrumentation for DTA Observability.
"""

import logging
from typing import Any, Optional

from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.instrumentation.utils import handle_instrumentation_error
from dta_observability.logging.logger import LoggingConfigurator, get_logger


class LoggingInstrumentor(BaseInstrumentor):
    """Handles logging instrumentation with OpenTelemetry integration."""

    _INSTRUMENTED_KEY = "_dta_logging_instrumented"

    def __init__(
        self,
        log_level: Optional[int] = logging.INFO,
        safe_logging: bool = True,
        log_format: Optional[str] = None,
    ):
        """Initialize the logging instrumentor."""
        super().__init__(log_level)
        self.safe_logging = safe_logging
        self.logger = get_logger("dta_observability.instrumentation")
        self.log_format = log_format

    def _get_library_name(self) -> str:
        """Get the library name."""
        return "logging"

    def instrument(self, app: Any = None) -> bool:
        """
        Set up logging instrumentation with JSON formatting and OpenTelemetry integration.

        Args:
            app: Not used for logging instrumentation, kept for API compatibility

        Returns:
            True if successful, False otherwise
        """

        if self.is_globally_instrumented():
            return True

        try:

            self._configure_json_formatting()

            self.set_globally_instrumented()
            return True
        except Exception as e:
            handle_instrumentation_error(self.logger, "logging", e, "instrumentation")
            return False

    def _configure_json_formatting(self) -> None:
        """
        Configure consistent JSON formatting for all loggers.

        This ensures that:
        1. All logs use the same formatting
        2. No mixed handlers exist
        3. All loggers use a consistent log level
        """
        log_level = self.log_level or logging.INFO

        self._clear_all_handlers()

        log_handler = LoggingConfigurator.create_handler(
            level=log_level,
            safe_logging=self.safe_logging,
            log_format=self.log_format,
        )

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        root_logger.addHandler(log_handler)
        LoggingConfigurator.configure_root_logger(log_level, log_handler)
        LoggingConfigurator.mark_configured()

    def _clear_all_handlers(self) -> None:
        """Remove all handlers from all loggers to prevent mixed logging."""

        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
