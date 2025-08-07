"""Download the latest Keycloak OpenAPI specification."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

import niquests


def download_openapi_spec():
    spec_url = "https://www.keycloak.org/docs-api/latest/rest-api/openapi.json"
    output_dir = Path(__file__).parent
    output_file = output_dir / "keycloak-openapi.json"
    metadata_file = output_dir / "keycloak-openapi-metadata.json"

    print(f"Downloading OpenAPI spec from {spec_url}")

    try:
        response = niquests.get(spec_url, timeout=30)
        response.raise_for_status()
    except niquests.RequestException as e:
        print(f"Error downloading spec: {e}")
        exit(1)

    spec_data = response.json()
    spec_text = json.dumps(spec_data, indent=2)
    new_hash = hashlib.sha256(spec_text.encode()).hexdigest()

    if metadata_file.exists():
        try:
            existing_metadata = json.loads(metadata_file.read_text())
            existing_hash = existing_metadata.get("sha256_hash")
            if existing_hash == new_hash:
                print(f"✅ OpenAPI spec is already up to date (hash: {new_hash[:8]}...)")
                return output_file
        except (json.JSONDecodeError, KeyError):
            pass

    output_file.write_text(spec_text)

    api_version = spec_data.get("info", {}).get("version", "unknown")

    metadata = {
        "download_url": spec_url,
        "download_date": datetime.now().isoformat(),
        "api_version": api_version,
        "spec_title": spec_data.get("info", {}).get("title", ""),
        "spec_description": spec_data.get("info", {}).get("description", ""),
        "paths_count": len(spec_data.get("paths", {})),
        "components_count": len(spec_data.get("components", {}).get("schemas", {})),
        "sha256_hash": new_hash
    }

    metadata_file.write_text(json.dumps(metadata, indent=2))

    print(
        f"✅ OpenAPI spec downloaded successfully to {output_file}\n"
        f"📊 Metadata saved to {metadata_file}\n"
        f"   - API Version: {api_version}\n"
        f"   - Paths: {metadata['paths_count']}\n"
        f"   - Components: {metadata['components_count']}\n"
        f"   - SHA256: {new_hash[:8]}..."
    )

    return output_file


if __name__ == "__main__":
    download_openapi_spec()
