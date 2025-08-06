"""
Resource detection for DTA Observability.
"""

import os
import socket
from typing import Any, Dict, List, Optional

from billiard import current_process  # type: ignore
from opentelemetry.resourcedetector.gcp_resource_detector import GoogleCloudResourceDetector
from opentelemetry.sdk.resources import Resource, ResourceDetector, get_aggregated_resources
from opentelemetry.semconv.resource import ResourceAttributes

from dta_observability.core.config import ConfigValueType, get_boolean_config, get_typed_config
from dta_observability.logging.logger import get_logger

logger = get_logger("dta_observability.resources")


def get_worker_id() -> str:
    """Get a consistent worker ID for instrumentation, matching container instrumentor.

    Returns:
        A string with hostname-processid format
    """
    process = current_process()
    process_id = getattr(process, "index", None)
    if process_id is None:
        process_id = os.getpid()

    return f"{socket.gethostname()}-{process_id}"


def _get_base_attributes() -> Dict[str, str]:
    """Get base service attributes from configuration."""
    attrs = {
        ResourceAttributes.SERVICE_NAME: get_typed_config("SERVICE_NAME", ConfigValueType.STRING, "unnamed-service"),
        ResourceAttributes.SERVICE_VERSION: get_typed_config("SERVICE_VERSION", ConfigValueType.STRING, "0.0.0"),
        ResourceAttributes.SERVICE_INSTANCE_ID: get_typed_config(
            "SERVICE_INSTANCE_ID", ConfigValueType.STRING, get_worker_id()
        ),
    }

    return attrs


def _get_cloud_provider() -> Optional[str]:
    """Determine the cloud provider from environment variables."""
    if os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT"):
        return "gcp"
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    if os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"):
        return "aws"
    if os.environ.get("AZURE_REGION") or os.environ.get("AZURE_LOCATION"):
        return "azure"
    return None


def _get_resource_detectors() -> List[ResourceDetector]:
    """Get list of resource detectors to use."""
    detectors: List[ResourceDetector] = []

    if _get_cloud_provider() == "gcp":
        try:
            detectors.append(GoogleCloudResourceDetector(raise_on_error=False))
            logger.debug("Added GoogleCloudResourceDetector to resource detectors")
        except Exception as e:
            logger.warning(f"Failed to initialize GoogleCloudResourceDetector: {e}")

    return detectors


def detect_resources(override_attrs: Optional[Dict[str, Any]] = None) -> Resource:
    """
    Detect resources from the environment.

    Args:
        override_attrs: Optional dictionary of attributes that override detected ones

    Returns:
        OpenTelemetry Resource with detected attributes.
    """

    if not get_boolean_config("RESOURCE_DETECTORS_ENABLED", default=True):
        logger.debug("Resource detection disabled via configuration")
        resource = Resource(override_attrs or {})
        return resource

    initial_resource = Resource(_get_base_attributes())
    resource = get_aggregated_resources(detectors=_get_resource_detectors(), initial_resource=initial_resource)

    if "cloud.provider" not in resource.attributes:
        cloud_provider = _get_cloud_provider()
        if cloud_provider:
            resource = resource.merge(Resource({"cloud.provider": cloud_provider}))

    if override_attrs:
        override_resource = Resource({k: v for k, v in override_attrs.items() if v is not None})
        resource = resource.merge(override_resource)

    logger.debug(f"Final resource attributes: {dict(resource.attributes)}")

    return resource
