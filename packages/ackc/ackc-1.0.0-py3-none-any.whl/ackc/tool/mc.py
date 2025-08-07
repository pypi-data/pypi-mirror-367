"""Keycloak management client CLI tool.

Maps the KeycloakManagementClient to a command-line interface for easy access to Keycloak management operations.
"""
import argparse
import json
import sys

from .. import env
from ..management import KeycloakManagementClient


def handle_health(client: KeycloakManagementClient, args) -> None:
    """Handle health commands."""
    probe_type = args.health_type or "overall"
    
    if probe_type == "live":
        response = client.health_live()
    elif probe_type == "ready":
        response = client.health_ready()
    elif probe_type == "started":
        response = client.health_started()
    else:
        response = client.health()
    
    if args.json:
        output = response.to_dict()
        output["probe"] = probe_type
        print(json.dumps(output, indent=2))
    else:
        status_line = f"[{probe_type.upper()}] Status: {response.status}"
        if response.checks:
            checks_info = " (" + ", ".join(f"{check.name}: {check.status}" for check in response.checks) + ")"
            print(status_line + checks_info)
        else:
            print(status_line)


def handle_metrics(client: KeycloakManagementClient, args) -> None:
    """Handle metrics command."""
    if args.json:
        metrics = client.metrics_parsed()
        print(json.dumps(metrics, indent=2))
    else:
        print(client.metrics())


def main():
    parser = argparse.ArgumentParser(
        description="Keycloak Management Client - Access health and metrics endpoints",
        prog="auth-mc"
    )
    
    parser.add_argument(
        "--url",
        help="Management interface URL (defaults to KEYCLOAK_MANAGEMENT_URL)",
        default=env.KEYCLOAK_MANAGEMENT_URL
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    health_parser = subparsers.add_parser("health", help="Check health status")
    health_subparsers = health_parser.add_subparsers(dest="health_type", help="Health check type")

    health_subparsers.add_parser("live", help="Check liveness probe")
    health_subparsers.add_parser("ready", help="Check readiness probe")
    health_subparsers.add_parser("started", help="Check started probe")

    subparsers.add_parser("metrics", help="Get Prometheus metrics")
    
    args = parser.parse_args()
    
    try:
        client = KeycloakManagementClient(url=args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.command == "health":
            handle_health(client, args)
        elif args.command == "metrics":
            handle_metrics(client, args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
