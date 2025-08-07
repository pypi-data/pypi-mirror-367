"""Generate Keycloak client with niquests HTTP backend.

This script automates the generation of a high-performance Keycloak client
using openapi-python-client with custom templates that use niquests instead
of httpx for better performance and HTTP/2 support.
"""
import argparse
import shutil
import subprocess
from pathlib import Path

from download_openapi import download_openapi_spec


def generate_client(download=False):
    """Generate the Keycloak client with niquests backend."""
    root_dir = Path(__file__).parent.parent
    templates_dir = root_dir / "gen" / "templates"
    openapi_spec = root_dir / "gen" / "keycloak-openapi.json"
    config_file = root_dir / "gen" / "openapi-config.yaml"
    output_dir = root_dir / "ackc" / "generated"

    if download or not openapi_spec.exists():
        download_openapi_spec()
        if not openapi_spec.exists():
            print("ERROR: Failed to download OpenAPI specification.")
            exit(1)

    if output_dir.exists():
        print(f"Cleaning existing generated files at {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating client from {openapi_spec}")
    cmd = [
        "openapi-python-client",
        "generate",
        "--path", str(openapi_spec),
        "--custom-template-path", str(templates_dir),
        "--output-path", str(output_dir),
        "--config", str(config_file)
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(result.stderr)
        exit(1)

    print(result.stdout.strip())

    generated_client = output_dir / "keycloak_admin_rest_api_client"
    if generated_client.exists():
        print(f"Moving generated client from {generated_client} to {output_dir}")
        for item in generated_client.iterdir():
            shutil.move(str(item), str(output_dir / item.name))
        generated_client.rmdir()

    (output_dir / "pyproject.toml").unlink(missing_ok=True)
    (output_dir / "README.md").unlink(missing_ok=True)

    print(f"✅ Client generated successfully at {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Keycloak client from OpenAPI spec")
    parser.add_argument(
        "-d", "--download",
        action="store_true",
        help="Download the latest OpenAPI specification before generating"
    )
    args = parser.parse_args()
    generate_client(download=args.download)
