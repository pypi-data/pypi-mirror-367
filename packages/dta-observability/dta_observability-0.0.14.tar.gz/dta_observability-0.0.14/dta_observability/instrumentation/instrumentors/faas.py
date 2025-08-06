"""
Function as a Service (FaaS) metrics instrumentation using OpenTelemetry.
"""

import os
import resource
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional, Tuple

from opentelemetry.metrics import CallbackOptions, Counter, Histogram, Meter, Observation
from opentelemetry.sdk.resources import Resource

from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.logging.logger import get_logger

FAAS_COLDSTARTS = "faas.coldstarts"
FAAS_CPU_USAGE = "faas.cpu_usage"
FAAS_ERRORS = "faas.errors"
FAAS_INIT_DURATION = "faas.init_duration"
FAAS_INVOCATIONS = "faas.invocations"
FAAS_INVOKE_DURATION = "faas.invoke_duration"
FAAS_MEM_USAGE = "faas.mem_usage"
FAAS_NET_IO = "faas.net_io"
FAAS_TIMEOUTS = "faas.timeouts"


class FaasInstrumentor(BaseInstrumentor):
    """Instrumentor for Function as a Service (FaaS) metrics.

    This instrumentor collects metrics specific to serverless function environments,
    such as AWS Lambda, Google Cloud Functions, or Azure Functions.
    """

    def __init__(
        self,
        log_level=None,
        resource_attributes: Optional[Resource] = None,
        config: Optional[Dict[str, Any]] = None,
        meter: Optional[Meter] = None,
    ) -> None:
        super().__init__(log_level)
        self._meter: Optional[Meter] = meter
        self._coldstarts_counter: Optional[Counter] = None
        self._cpu_usage_histogram: Optional[Histogram] = None
        self._errors_counter: Optional[Counter] = None
        self._init_duration_histogram: Optional[Histogram] = None
        self._invocations_counter: Optional[Counter] = None
        self._invoke_duration_histogram: Optional[Histogram] = None
        self._mem_usage_histogram: Optional[Histogram] = None
        self._net_io_histogram: Optional[Histogram] = None
        self._timeouts_counter: Optional[Counter] = None

        self._function_name: str = "unknown_function"
        self._start_time = time.time()
        self._cold_start = True
        self._invoke_start_times: Dict[str, Tuple[float, float, int, int]] = {}
        self._active_invocations: set[str] = set()
        self._metrics_lock = threading.RLock()

        self.resource_attributes: Optional[Resource] = resource_attributes
        self.config = config or {}
        self._logger = get_logger("dta_observability.instrumentation.faas")

    def _get_library_name(self) -> str:
        """Get the name of the library being instrumented."""
        return "faas"

    def instrument(self, app: Any = None) -> bool:
        """
        Instrument FaaS metrics collection.

        Args:
            app: Not used for FaaS metrics, but required by interface

        Returns:
            True if instrumentation was successful, False otherwise
        """

        if not self._is_in_faas():
            self._logger.info("Not running in a FaaS environment, skipping FaaS metrics instrumentation")
            return False

        self._init_faas_environment()

        if self._meter is None:
            self._logger.warning("Failed to get meter for FaaS metrics")
            return False

        self._create_metrics()

        had_cold_start = self._cold_start
        self._cold_start = False

        if had_cold_start:
            self._logger.info(f"Cold start detected for function: {self._function_name}")

            self._meter.create_observable_gauge(
                name=f"{FAAS_COLDSTARTS}_detected",
                description="Cold start detection",
                unit="{coldstart}",
                callbacks=[self._observe_cold_start],
            )

        self._logger.info(f"FaaS metrics instrumentation enabled for function: {self._function_name}")
        return True

    def _is_in_faas(self) -> bool:
        """Check if we're running in a FaaS/serverless environment."""

        faas_env_vars = [
            "FUNCTION_NAME",
            "K_SERVICE",
        ]

        if faas_env_vars:
            return any(env in os.environ for env in faas_env_vars)

        return False

    def _init_faas_environment(self) -> None:
        """Initialize FaaS environment details."""

        self._function_name = (
            os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
            or os.environ.get("FUNCTION_NAME")
            or os.environ.get("FUNCTION_TARGET")
            or os.environ.get("K_SERVICE")
            or "unknown_function"
        )

        self._is_aws = "AWS_LAMBDA_FUNCTION_NAME" in os.environ
        self._is_gcp_function = "FUNCTION_NAME" in os.environ and "FUNCTION_TARGET" in os.environ
        self._is_cloud_run = "K_SERVICE" in os.environ and "K_REVISION" in os.environ
        self._is_gcp = self._is_gcp_function or self._is_cloud_run
        self._is_azure = "FUNCTIONS_WORKER_RUNTIME" in os.environ

        self._cpu_time_start = self._get_cpu_time()
        self._mem_usage_start = self._get_memory_usage()
        self._net_io_start = self._get_network_io()

    def _create_metrics(self) -> None:
        """Create all FaaS metrics."""
        if self._meter is None:
            self._logger.warning("No meter available for creating FaaS metrics")
            return

        self._coldstarts_counter = self._meter.create_counter(
            name=FAAS_COLDSTARTS,
            description="Number of invocation cold starts",
            unit="{coldstart}",
        )

        self._meter.create_observable_gauge(
            name=FAAS_CPU_USAGE,
            description="Current CPU usage",
            unit="s",
            callbacks=[self._observe_cpu_usage],
        )

        self._cpu_usage_histogram = self._meter.create_histogram(
            name=f"{FAAS_CPU_USAGE}_duration",
            description="Distribution of CPU usage per invocation",
            unit="s",
        )

        self._errors_counter = self._meter.create_counter(
            name=FAAS_ERRORS,
            description="Number of invocation errors",
            unit="{error}",
        )

        self._init_duration_histogram = self._meter.create_histogram(
            name=FAAS_INIT_DURATION,
            description="Measures the duration of the function's initialization, such as a cold start",
            unit="s",
        )

        self._invocations_counter = self._meter.create_counter(
            name=FAAS_INVOCATIONS,
            description="Number of successful invocations",
            unit="{invocation}",
        )

        self._invoke_duration_histogram = self._meter.create_histogram(
            name=FAAS_INVOKE_DURATION,
            description="Measures the duration of the function's logic execution",
            unit="s",
        )

        self._meter.create_observable_gauge(
            name=FAAS_MEM_USAGE,
            description="Current memory usage",
            unit="By",
            callbacks=[self._observe_memory_usage],
        )

        self._mem_usage_histogram = self._meter.create_histogram(
            name=f"{FAAS_MEM_USAGE}_max",
            description="Distribution of max memory usage per invocation",
            unit="By",
        )

        self._meter.create_observable_gauge(
            name=FAAS_NET_IO,
            description="Current network I/O",
            unit="By",
            callbacks=[self._observe_network_io],
        )

        self._net_io_histogram = self._meter.create_histogram(
            name=f"{FAAS_NET_IO}_total",
            description="Distribution of net I/O usage per invocation",
            unit="By",
        )

        self._timeouts_counter = self._meter.create_counter(
            name=FAAS_TIMEOUTS,
            description="Number of invocation timeouts",
            unit="{timeout}",
        )

    def _get_common_attributes(self, extra_attributes: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get common attributes for metrics including resource attributes.

        Args:
            extra_attributes: Additional attributes to include

        Returns:
            Dict of common attributes
        """
        attributes = {"function.name": self._function_name}

        if hasattr(self, "_is_aws") and self._is_aws:
            attributes["cloud.provider"] = "aws"
        elif hasattr(self, "_is_gcp") and self._is_gcp:
            attributes["cloud.provider"] = "gcp"
        elif hasattr(self, "_is_azure") and self._is_azure:
            attributes["cloud.provider"] = "azure"

        if self.resource_attributes:
            attributes.update({k: str(v) for k, v in self.resource_attributes.attributes.items() if v is not None})

        if extra_attributes:
            attributes.update(extra_attributes)

        return attributes

    def _get_cpu_time(self) -> float:
        """Get current CPU time usage in seconds."""
        try:
            return sum(resource.getrusage(resource.RUSAGE_SELF)[0:2])
        except Exception as e:
            self._logger.debug(f"Failed to get CPU time: {e}")
            return 0.0

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:

            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        except Exception as e:
            self._logger.debug(f"Failed to get memory usage: {e}")
            return 0

    def _get_network_io(self) -> int:
        """Get current network I/O usage in bytes."""
        try:

            with open("/proc/self/net/dev", "r") as f:
                lines = f.readlines()[2:]
                total_bytes = 0
                for line in lines:

                    parts = line.split(":")
                    if len(parts) != 2:
                        continue
                    values = parts[1].strip().split()
                    if len(values) < 9:
                        continue
                    rx_bytes = int(values[0])
                    tx_bytes = int(values[8])
                    total_bytes += rx_bytes + tx_bytes
                return total_bytes
        except (IOError, FileNotFoundError, ValueError, IndexError):
            return 0

    @contextmanager
    def track_invocation(self, invocation_id: Optional[str] = None):
        """
        Context manager to track a function invocation.

        Args:
            invocation_id: Optional unique identifier for this invocation

        Yields:
            None
        """

        if not self._invocations_counter:
            yield
            return

        if invocation_id is None:
            invocation_id = f"inv-{time.time()}-{id(threading.current_thread())}"

        attributes = self._get_common_attributes({"invocation.id": invocation_id})

        if hasattr(self, "_is_aws") and self._is_aws:
            request_id = os.environ.get("AWS_LAMBDA_REQUEST_ID")
            if request_id:
                attributes["faas.invocation_id"] = request_id

        start_cpu_time = self._get_cpu_time()
        start_mem_usage = self._get_memory_usage()
        start_net_io = self._get_network_io()
        start_time = time.time()

        with self._metrics_lock:
            self._active_invocations.add(invocation_id)
            self._invoke_start_times[invocation_id] = (start_time, start_cpu_time, start_mem_usage, start_net_io)

        try:

            yield

            self._invocations_counter.add(1, attributes)
        except Exception as e:

            if self._errors_counter:
                error_attributes = attributes.copy()
                error_attributes["error.type"] = e.__class__.__name__
                self._errors_counter.add(1, error_attributes)
            raise
        finally:

            end_time = time.time()
            end_cpu_time = self._get_cpu_time()
            end_mem_usage = self._get_memory_usage()
            end_net_io = self._get_network_io()

            if self._invoke_duration_histogram:
                invoke_duration = end_time - start_time
                self._invoke_duration_histogram.record(invoke_duration, attributes)

            if self._cpu_usage_histogram:
                cpu_usage = end_cpu_time - start_cpu_time
                self._cpu_usage_histogram.record(cpu_usage, attributes)

            if self._mem_usage_histogram:
                mem_usage = end_mem_usage
                self._mem_usage_histogram.record(mem_usage, attributes)

            if self._net_io_histogram:
                net_io = end_net_io - start_net_io
                self._net_io_histogram.record(net_io, attributes)

            with self._metrics_lock:
                if invocation_id in self._active_invocations:
                    self._active_invocations.remove(invocation_id)
                if invocation_id in self._invoke_start_times:
                    del self._invoke_start_times[invocation_id]

            self._logger.debug(
                f"Function {self._function_name} invocation {invocation_id} completed "
                f"in {end_time - start_time:.6f}s"
            )

    def _observe_cpu_usage(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for CPU usage observation."""

        attrs = self._get_common_attributes()

        try:
            cpu_time = self._get_cpu_time()

            with self._metrics_lock:
                yield Observation(value=cpu_time, attributes=attrs)
        except Exception as e:
            self._logger.warning(f"Error observing CPU usage: {e}", exc_info=True)

            with self._metrics_lock:
                yield Observation(value=0.0, attributes=attrs)

    def _observe_memory_usage(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for memory usage observation."""

        attrs = self._get_common_attributes()

        try:
            memory_usage = self._get_memory_usage()
            with self._metrics_lock:
                yield Observation(value=memory_usage, attributes=attrs)
        except Exception as e:
            self._logger.warning(f"Error observing memory usage: {e}", exc_info=True)
            with self._metrics_lock:
                yield Observation(value=0.0, attributes=attrs)

    def _observe_network_io(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for network I/O observation."""

        attrs = self._get_common_attributes()

        try:
            net_io = self._get_network_io()

            with self._metrics_lock:
                yield Observation(value=net_io, attributes=attrs)
        except Exception as e:
            self._logger.warning(f"Error observing network I/O: {e}", exc_info=True)

            with self._metrics_lock:
                yield Observation(value=0.0, attributes=attrs)

    def _observe_cold_start(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for cold start observation."""

        attrs = self._get_common_attributes()

        try:

            init_duration = time.time() - self._start_time

            if self._coldstarts_counter and not hasattr(self, "_cold_start_recorded"):

                self._coldstarts_counter.add(1, attrs)

                if self._init_duration_histogram:
                    self._init_duration_histogram.record(init_duration, attrs)

                self._logger.info(
                    f"Recorded cold start for function {self._function_name} with init duration: {init_duration:.6f}s"
                )
                self._cold_start_recorded = True

            with self._metrics_lock:
                yield Observation(value=1.0, attributes=attrs)

        except Exception:
            with self._metrics_lock:
                yield Observation(value=0.0, attributes=attrs)

    def record_timeout(self, invocation_id: Optional[str] = None):
        """
        Record a function timeout.

        Args:
            invocation_id: Optional unique identifier for the invocation that timed out
        """
        if not self._timeouts_counter:
            return

        extra_attributes = {"invocation.id": invocation_id} if invocation_id else None
        attributes = self._get_common_attributes(extra_attributes)

        self._timeouts_counter.add(1, attributes)
        self._logger.info(f"Recorded timeout for function {self._function_name}")
