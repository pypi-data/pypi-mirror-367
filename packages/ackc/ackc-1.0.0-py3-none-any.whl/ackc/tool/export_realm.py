import argparse
import json
import sys

from .. import env
from ..exceptions import AuthError
from ..keycloak import KeycloakClient


def main():
    parser = argparse.ArgumentParser(description="Export Keycloak realm configuration")

    parser.add_argument("realm", help="Realm name to export")

    parser.add_argument("--server-url",
                        default=env.KEYCLOAK_URL,
                        help="Keycloak server URL (default: KEYCLOAK_URL)")

    parser.add_argument("--client-id",
                        default=env.KEYCLOAK_CLIENT_ID,
                        help="Client ID (default: KEYCLOAK_CLIENT_ID)")

    parser.add_argument("--client-secret",
                        default=env.KEYCLOAK_CLIENT_SECRET,
                        help="Client secret (default: KEYCLOAK_CLIENT_SECRET)")

    parser.add_argument("--include-users",
                        action="store_true",
                        help="Include users in export")

    parser.add_argument("--pretty",
                        action="store_true",
                        help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        client = KeycloakClient(
            server_url=args.server_url,
            client_id=args.client_id,
            client_secret=args.client_secret,
        )

        print(f"Exporting realm: {args.realm}", file=sys.stderr)

        config = client.export_realm_config(args.realm, include_users=args.include_users)

        if args.pretty:
            print(json.dumps(config, indent=2))
        else:
            print(json.dumps(config))

    except AuthError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
