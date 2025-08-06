"""
Container metrics instrumentation using OpenTelemetry.
"""

import os
import socket
import threading
from typing import Any, Dict, Iterable, Optional

from billiard import current_process  # type: ignore

try:
    import psutil
    from psutil import AccessDenied, NoSuchProcess

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


from opentelemetry.metrics import CallbackOptions, Meter, Observation
from opentelemetry.sdk.resources import Resource

from dta_observability.instrumentation.base import BaseInstrumentor
from dta_observability.logging.logger import get_logger

CONTAINER_CPU_USAGE = "container.cpu.usage"
CONTAINER_MEMORY_USAGE = "container.memory.usage"
CONTAINER_DISK_IO = "container.disk.io"
CONTAINER_NETWORK_IO = "container.network.io"


CPU_TYPE_LABEL = "cpu.type"
CPU_MODE_LABEL = "cpu.mode"
MEMORY_TYPE_LABEL = "memory.type"
MEMORY_STATE_LABEL = "memory.state"


def _get_cpu_usage() -> Dict[str, float]:
    """Get CPU usage percentages."""
    if not HAS_PSUTIL:
        return {}

    cpu_usage = {}
    try:
        cpu_percents = psutil.cpu_percent(interval=None, percpu=True)
        for cpu_num, cpu_percent in enumerate(cpu_percents):
            cpu_usage[f"cpu{cpu_num}"] = cpu_percent / 100.0

    except (AccessDenied, NoSuchProcess) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Access denied when getting CPU usage: {e}", exc_info=True
        )
    except Exception as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Failed to get CPU usage: {e}", exc_info=True
        )

    return cpu_usage


def _get_memory_metrics() -> Dict[str, float]:
    """Get memory metrics."""
    if not HAS_PSUTIL:
        return {}

    memory_data = {}
    try:
        mem = psutil.virtual_memory()

        mem_types = ["available", "used", "free", "active", "inactive", "buffers", "cached", "shared", "slab"]

        for name in mem_types:
            if hasattr(mem, name):
                value = getattr(mem, name)
                if isinstance(value, (int, float)):
                    memory_data[f"virtual_{name}"] = float(value)

    except (AccessDenied, NoSuchProcess) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Access denied when getting memory metrics: {e}", exc_info=True
        )
    except Exception as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Failed to get memory metrics: {e}", exc_info=True
        )

    return memory_data


def _get_disk_io_metric() -> Optional[int]:
    """Get disk I/O metric (total bytes read and written)."""
    if not HAS_PSUTIL:
        return None

    try:
        disk_io = psutil.disk_io_counters()
        if disk_io:
            return disk_io.read_bytes + disk_io.write_bytes
    except (AccessDenied, NoSuchProcess) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Access denied when getting disk I/O metric: {e}", exc_info=True
        )
    except (AttributeError, OSError, Exception) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Failed to get disk I/O metric: {e}", exc_info=True
        )

    return None


def _get_network_io_metric() -> Optional[int]:
    """Get network I/O metric (total bytes sent and received)."""
    if not HAS_PSUTIL:
        return None

    try:
        net_io = psutil.net_io_counters()
        if net_io:
            return net_io.bytes_sent + net_io.bytes_recv
    except (AccessDenied, NoSuchProcess) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Access denied when getting network I/O metric: {e}", exc_info=True
        )
    except (AttributeError, OSError, Exception) as e:
        get_logger("dta_observability.instrumentation.container").warning(
            f"Failed to get network I/O metric: {e}", exc_info=True
        )

    return None


class ContainerInstrumentor(BaseInstrumentor):
    """Instrumentor for container metrics in containerized environments."""

    def __init__(
        self,
        log_level=None,
        resource_attributes: Optional[Resource] = None,
        meter: Optional[Meter] = None,
    ) -> None:
        super().__init__(log_level)
        self._meter: Optional[Meter] = meter
        self._counters: Dict[str, Optional[Any]] = {"cpu": None, "memory": None, "disk": None, "network": None}
        self._metrics_lock = threading.RLock()
        self._logger = get_logger("dta_observability.instrumentation.container")
        self.resource_attributes: Optional[Resource] = resource_attributes

        self._service_instance_id = None
        if resource_attributes:
            from opentelemetry.sdk.resources import ResourceAttributes

            if (
                hasattr(resource_attributes, "attributes")
                and ResourceAttributes.SERVICE_INSTANCE_ID in resource_attributes.attributes
            ):
                self._service_instance_id = resource_attributes.attributes[ResourceAttributes.SERVICE_INSTANCE_ID]
                self._logger.debug(f"Using service.instance.id: {self._service_instance_id}")

    def _get_library_name(self) -> str:
        """Get the name of the library being instrumented."""
        return "container"

    def instrument(self, app: Any = None) -> bool:
        """Set up container metrics instrumentation."""

        if not self._is_in_container():
            self._logger.info("Not running in a container environment")
            return False

        if not HAS_PSUTIL:
            self._logger.warning("psutil package not available")
            return False

        self._create_metrics()

        self._logger.info("Container metrics instrumentation completed")
        return True

    def _is_in_container(self) -> bool:
        """Check if running in a container environment."""

        if "KUBERNETES_SERVICE_HOST" in os.environ:
            return True

        if os.path.exists("/.dockerenv"):
            return True

        if os.path.exists("/var/run/secrets/kubernetes.io"):
            return True

        return False

    def _observe_memory_usage(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for memory usage observation."""
        if not HAS_PSUTIL:
            return

        with self._metrics_lock:

            try:
                memory_data = _get_memory_metrics()
                memory_metrics = {}

                base_attributes = self._get_base_attributes()

                for name, value in memory_data.items():
                    mem_type, mem_state = name.split("_", 1)
                    attrs = {MEMORY_TYPE_LABEL: mem_type, MEMORY_STATE_LABEL: mem_state}
                    attrs.update(base_attributes)
                    memory_metrics[name] = (value, attrs)

                for value, attrs in memory_metrics.values():
                    yield Observation(value=value, attributes=attrs)

            except Exception as e:
                self._logger.error(f"Error observing memory usage: {e}", exc_info=True)
                attributes = self._get_base_attributes()
                attributes["error"] = str(e)
                attributes["error_type"] = e.__class__.__name__

                yield Observation(value=0.0, attributes=attributes)

    def _observe_disk_io(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for disk I/O observation."""
        if not HAS_PSUTIL:
            return

        with self._metrics_lock:
            try:
                disk_val = _get_disk_io_metric()
                value = disk_val if disk_val is not None else 0.0
                attributes = self._get_base_attributes()

                yield Observation(value=value, attributes=attributes)

            except Exception as e:
                self._logger.error(f"Error observing disk I/O: {e}", exc_info=True)
                attributes = self._get_base_attributes()
                attributes["error"] = str(e)
                attributes["error_type"] = e.__class__.__name__

                yield Observation(value=0.0, attributes=attributes)

    def _observe_network_io(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for network I/O observation."""
        if not HAS_PSUTIL:
            return

        with self._metrics_lock:
            try:
                net_val = _get_network_io_metric()
                value = net_val if net_val is not None else 0.0
                attributes = self._get_base_attributes()

                yield Observation(value=value, attributes=attributes)

            except Exception as e:
                self._logger.error(f"Error observing network I/O: {e}", exc_info=True)
                attributes = self._get_base_attributes()
                attributes["error"] = str(e)
                attributes["error_type"] = e.__class__.__name__

                yield Observation(value=0.0, attributes=attributes)

    def _observe_cpu_usage(self, options: CallbackOptions) -> Iterable[Observation]:
        """Callback for CPU usage observation."""
        if not HAS_PSUTIL:
            return

        with self._metrics_lock:
            try:
                cpu_usage = _get_cpu_usage()
                observations = {}
                base_attributes = self._get_base_attributes()

                for cpu_id, cpu_percent in cpu_usage.items():
                    attrs = {CPU_MODE_LABEL: cpu_id}
                    attrs.update(base_attributes)
                    observations[cpu_id] = (cpu_percent, attrs)

                for value, attrs in observations.values():
                    yield Observation(value=value, attributes=attrs)

            except Exception as e:
                self._logger.error(f"Error observing CPU usage: {e}", exc_info=True)
                attributes = self._get_base_attributes()
                attributes["error"] = str(e)
                attributes["error_type"] = e.__class__.__name__

                yield Observation(value=0.0, attributes=attributes)

    def _create_metrics(self) -> None:
        """Create all container metrics with retry logic."""
        if self._meter is None:
            return

        try:
            cpu_usage_callbacks = [self._observe_cpu_usage]
            self._meter.create_observable_gauge(
                name=CONTAINER_CPU_USAGE,
                callbacks=cpu_usage_callbacks,
                description="CPU usage by core",
                unit="{cpu}",
            )

            memory_callbacks = [self._observe_memory_usage]
            self._meter.create_observable_gauge(
                name=CONTAINER_MEMORY_USAGE,
                callbacks=memory_callbacks,
                description="Memory usage by type and state",
                unit="By",
            )

            disk_callbacks = [self._observe_disk_io]
            self._meter.create_observable_gauge(
                name=CONTAINER_DISK_IO,
                callbacks=disk_callbacks,
                description="Disk bytes (read+write)",
                unit="By",
            )

            network_callbacks = [self._observe_network_io]
            self._meter.create_observable_gauge(
                name=CONTAINER_NETWORK_IO,
                callbacks=network_callbacks,
                description="Network bytes (sent+received)",
                unit="By",
            )

            self._counters = {}

        except Exception as e:
            self._logger.error(f"Failed to create metrics: {e}", exc_info=True)

    def _get_base_attributes(self) -> Dict[str, Any]:
        """Get base attributes for all metrics, including service.instance.id if available."""
        attributes = {}

        attributes["service.instance.id"] = self._service_instance_id
        process = current_process()

        process_id = getattr(process, "index", None)
        if process_id is None:
            process_id = os.getpid()

        prefork_worker = f"{socket.gethostname()}-{process_id}"
        attributes["service.instance.worker"] = prefork_worker

        return attributes
