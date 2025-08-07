"""
Keycloak Management Interface API client.

This module provides access to the Keycloak management interface endpoints
(health, metrics) that are exposed on port 9000 by default.
"""
import os
from typing import Any, Literal
from urllib.parse import urljoin

import attrs
from niquests import Response

from .api import AuthenticatedClient, Client
from . import env

__all__ = [
    "KeycloakManagementClient",
    "HealthStatus",
    "HealthCheck",
    "HealthResponse",
]

HealthStatus = Literal["UP", "DOWN"]


@attrs.define
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthStatus
    data: dict[str, Any] = attrs.field(factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {"name": self.name, "status": self.status}
        if self.data:
            result["data"] = self.data
        return result


@attrs.define
class HealthResponse:
    """Health check response."""

    status: HealthStatus
    checks: list[HealthCheck] = attrs.field(factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status,
            "checks": [check.to_dict() for check in self.checks]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HealthResponse":
        """Create from dictionary representation."""
        checks = [
            HealthCheck(
                name=check["name"],
                status=check["status"],
                data=check.get("data", {})
            )
            for check in data.get("checks", [])
        ]
        return cls(status=data["status"], checks=checks)


class KeycloakManagementClient:
    """Client for Keycloak management interface endpoints.
    
    This client can work with either regular Client or AuthenticatedClient.
    Authentication is typically not required for management endpoints when
    accessed from within the Keycloak network/container.
    """
    _client_config: dict[str, Any]
    _client: Client | AuthenticatedClient | None = None

    def __init__(
        self,
        url: str | None = None,
        verify_ssl: bool = True,
        timeout: float = 30.0,
        headers: dict[str, str] | None = None,
        client: Client | AuthenticatedClient | None = None,
    ):
        """
        Initialize the management client.
        
        Args:
            url: Management interface URL (defaults to KEYCLOAK_MANAGEMENT_URL)
                 Example: http://localhost:9000 or http://localhost:9000/management
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
            headers: Additional headers to include in requests
            client: Optional pre-configured client (Client or AuthenticatedClient)
        """
        self.url = url or env.KEYCLOAK_MANAGEMENT_URL
        if not self.url:
            raise ValueError(
                "Management URL required. Set KEYCLOAK_MANAGEMENT_URL env var or pass url parameter."
            )

        self._client_config = {
            "base_url": self.url,
            "verify_ssl": verify_ssl,
            "timeout": timeout,
            "headers": headers or {},
        }

        if client is not None:
            if not isinstance(client, (Client, AuthenticatedClient)):
                raise TypeError("client must be an instance of Client or AuthenticatedClient")  # noqa: This is reachable if caller passes an invalid type
            self._client = client

    @property
    def client(self) -> Client | AuthenticatedClient:
        if self._client is None:
            self._client = Client(**self._client_config)
        return self._client

    def _get(self, endpoint: str) -> Response:
        """Make a synchronous request to a management endpoint."""
        client = self.client
        url = urljoin(self.url, endpoint.lstrip("/"))

        with client:
            return client.get_niquests_client().get(url)

    async def _aget(self, endpoint: str) -> Response:
        """Make an asynchronous request to a management endpoint."""
        client = self.client
        url = urljoin(self.url, endpoint.lstrip("/"))

        async with client:
            return await client.get_async_niquests_client().get(url)

    def health(self) -> HealthResponse:
        """Get overall health status."""
        response = self._get("/health")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    async def ahealth(self) -> HealthResponse:
        """Get overall health status (async)."""
        response = await self._aget("/health")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    def health_live(self) -> HealthResponse:
        """Get liveness probe status."""
        response = self._get("/health/live")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    async def ahealth_live(self) -> HealthResponse:
        """Get liveness probe status (async)."""
        response = await self._aget("/health/live")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    def health_ready(self) -> HealthResponse:
        """Get readiness probe status."""
        response = self._get("/health/ready")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    async def ahealth_ready(self) -> HealthResponse:
        """Get readiness probe status (async)."""
        response = await self._aget("/health/ready")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    def health_started(self) -> HealthResponse:
        """Get started probe status."""
        response = self._get("/health/started")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    async def ahealth_started(self) -> HealthResponse:
        """Get started probe status (async)."""
        response = await self._aget("/health/started")
        response.raise_for_status()
        return HealthResponse.from_dict(response.json())

    def metrics(self) -> str:
        """Get Prometheus metrics in OpenMetrics format."""
        response = self._get("/metrics")
        response.raise_for_status()
        return response.text

    async def ametrics(self) -> str:
        """Get Prometheus metrics in OpenMetrics format (async)."""
        response = await self._aget("/metrics")
        response.raise_for_status()
        return response.text

    def metrics_parsed(self) -> dict[str, Any]:
        """Get Prometheus metrics parsed into a dictionary.
        
        Returns:
            Dictionary with metric names as keys and their values/metadata
        """
        metrics_text = self.metrics()
        return self._parse_prometheus_metrics(metrics_text)

    async def ametrics_parsed(self) -> dict[str, Any]:
        """Get Prometheus metrics parsed into a dictionary (async).
        
        Returns:
            Dictionary with metric names as keys and their values/metadata
        """
        metrics_text = await self.ametrics()
        return self._parse_prometheus_metrics(metrics_text)

    def _parse_prometheus_metrics(self, metrics_text: str) -> dict[str, Any]:
        """Parse Prometheus metrics text format into dictionary."""
        metrics = {}
        current_metric = None

        for line in metrics_text.strip().split("\n"):
            line = line.strip()

            if not line or line.startswith("#"):
                if line.startswith("# HELP"):
                    parts = line.split(" ", 3)
                    if len(parts) >= 4:
                        metric_name = parts[2]
                        help_text = parts[3]
                        metrics[metric_name] = {"help": help_text, "values": []}
                        current_metric = metric_name
                elif line.startswith("# TYPE"):
                    parts = line.split(" ", 3)
                    if len(parts) >= 4 and current_metric:
                        metrics[current_metric]["type"] = parts[3]
            else:
                if " " in line:
                    metric_with_labels, value = line.rsplit(" ", 1)
                    try:
                        value = float(value)
                    except ValueError:
                        continue

                    if "{" in metric_with_labels:
                        metric_name, labels_str = metric_with_labels.split("{", 1)
                        labels_str = labels_str.rstrip("}")
                        labels = {}

                        for label_pair in labels_str.split(","):
                            if "=" in label_pair:
                                key, val = label_pair.split("=", 1)
                                labels[key.strip()] = val.strip("\"")
                    else:
                        metric_name = metric_with_labels
                        labels = {}

                    if metric_name in metrics:
                        metrics[metric_name]["values"].append({
                            "value": value,
                            "labels": labels
                        })

        return metrics
