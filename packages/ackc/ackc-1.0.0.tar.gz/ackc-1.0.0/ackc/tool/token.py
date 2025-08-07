"""Keycloak token acquisition tool.

This module provides both a CLI tool and reusable functions for obtaining
Keycloak tokens via various OAuth2 flows (client credentials, password, device).

It was made with the idea that token acquisition ana management tools can build on it for
more advanced use cases, such as Django management commands or orgnaization-specific CLI login
management.

CLI Usage:
    auth-token                      # Client credentials
    auth-token client               # Client credentials (explicit)
    auth-token device               # Device flow
    auth-token password -u admin    # Password flow
    auth-token refresh TOKEN        # Refresh a token
    auth-token -q                   # Just the token
    auth-token --decode             # Show JWT claims

Library Usage:
    from ackc.tool.token import run
    
    # With dict args (e.g., from Django)
    token = run({"server_url": "https://keycloak.example.com", "command": "device"})
    
    # With custom client factory
    def my_factory(**kwds):
        return KeycloakClient(
            server_url=kwds.get("server_url") or settings.KEYCLOAK_URL,
            realm=kwds.get("realm") or settings.KEYCLOAK_REALM,
            client_id=kwds.get("client_id") or settings.KEYCLOAK_CLIENT_ID,
            client_secret=kwds.get("client_secret") or settings.KEYCLOAK_CLIENT_SECRET,
        )
    
    token = run(args, client_factory=my_factory)

Django Management Command Example:
    from django.core.management.base import BaseCommand
    from django.conf import settings
    from ackc.tool.token import init_parser, run, format_output
    from ackc import KeycloakClient
    
    class Command(BaseCommand):
        help = "Get Keycloak access token"
        
        def add_arguments(self, parser):
            init_parser(parser)
        
        def handle(self, *args, **options):
            def django_client_factory(**kwds):
                return KeycloakClient(
                    server_url=kwds.get("server_url") or settings.KEYCLOAK_URL,
                    realm=kwds.get("realm") or settings.KEYCLOAK_REALM,
                    client_id=kwds.get("client_id") or settings.KEYCLOAK_CLIENT_ID,
                    client_secret=kwds.get("client_secret") or settings.KEYCLOAK_CLIENT_SECRET,
                )

            token = run(options, client_factory=django_client_factory)
            output = format_output(token, options["quiet"], options["decode"])
            self.stdout.write(output)

"""
import argparse
import json
import sys
import webbrowser
from getpass import getpass

from .. import env
from ..exceptions import AuthError
from ..keycloak import KeycloakClient
from ..tokens import (
    get_token_client_credentials,
    get_token_device,
    get_token_password,
    get_token_refresh,
)


def init_parser(parser=None):
    """Create and return the argument parser for get_token.
    
    Args:
        parser: Optional existing ArgumentParser to add arguments to.
                If None, creates a new parser with description and epilog.
    
    Returns:
        ArgumentParser with all get_token arguments added.
    """
    if parser is None:
        parser = argparse.ArgumentParser(
            description="Get an access token from Keycloak",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  %(prog)s                           # Client credentials (default)
  %(prog)s client                    # Client credentials (explicit)
  %(prog)s device                    # Device flow (browser)
  %(prog)s password -u admin         # Password auth
  %(prog)s refresh TOKEN             # Refresh a token"""
        )

    parser.add_argument("--server-url", default=env.KEYCLOAK_URL, help="Keycloak server URL (default: KEYCLOAK_URL)")

    parser.add_argument(
        "--realm",
        default=None,
        help="Realm name (default: KEYCLOAK_REALM)"
    )

    parser.add_argument("--auth-realm", default=None, help="Realm for client authentication (defaults to --realm value)")
    parser.add_argument("--client-id", default=None, help="Client ID (default: KEYCLOAK_CLIENT_ID)")
    parser.add_argument("--client-secret", default=None, help="Client secret (default: KEYCLOAK_CLIENT_SECRET)")

    print_options = parser.add_mutually_exclusive_group()

    print_options.add_argument("-q", "--quiet", action="store_true", help="Output only the token value")
    print_options.add_argument("--decode", action="store_true", help="Decode and display JWT claims")

    subparsers = parser.add_subparsers(dest="command", help="Authentication method")

    client_parser = subparsers.add_parser("client", help="Client credentials flow (machine-to-machine)")
    client_parser.add_argument("--scopes", help="OAuth2 scopes (space-separated or comma-separated)")

    device_parser = subparsers.add_parser("device", help="Device authorization flow (browser-based)")
    device_parser.add_argument("--scopes", help="OAuth2 scopes (space-separated or comma-separated)")

    password_parser = subparsers.add_parser("password", help="Password grant flow (legacy)")
    password_parser.add_argument("-u", "--username", help="Username to authenticate")

    otp_group = password_parser.add_mutually_exclusive_group()
    otp_group.add_argument("--otp", action="store_true", help="Prompt for OTP/2FA code")
    otp_group.add_argument("--otp-code", help="Provide OTP/2FA code directly")

    password_parser.add_argument("--scopes", help="OAuth2 scopes (space-separated or comma-separated)")

    refresh_parser = subparsers.add_parser("refresh", help="Refresh an existing token")
    refresh_parser.add_argument("token", help="The refresh token to exchange")

    return parser


def create_device_callback(quiet=False):
    """Create a device callback function for CLI usage."""

    def device_callback(*, verification_uri, user_code, expires_in):
        if not quiet:
            print(f"Open browser to: {verification_uri}", file=sys.stderr)
            print(f"User code: {user_code}", file=sys.stderr)
            print(f"Expires in: {expires_in} seconds", file=sys.stderr)
        webbrowser.open(verification_uri)

    return device_callback


def format_output(*, token, quiet=False, decode=False):
    """Format token output based on options."""
    if quiet:
        return token.get("access_token", token)

    output = token.copy()

    if decode and "access_token" in token:
        claims = KeycloakClient.jwt_decode(jwt=token["access_token"])
        output["claims"] = claims

    return json.dumps(output, indent=2)


def get_credentials(args, request_otp=False):
    """Get credentials for password auth, prompting if needed."""
    username = args.username
    if not username:
        username = input("Username: " if not args.quiet else "")
    password = getpass(f"Password for {username}: " if not args.quiet else "")

    otp = None
    if request_otp:
        otp = getpass("OTP code: " if not args.quiet else "")

    return username, password, otp


def run(args, *, client_factory=None):
    """Run the token acquisition based on parsed arguments.
    
    Args:
        args: Parsed command line arguments (Namespace or dict)
        client_factory: Optional factory function for creating KeycloakClient instances
        
    Returns:
        Token dict with access_token, refresh_token, etc.
    """
    if isinstance(args, dict):
        args = argparse.Namespace(**args)

    scopes = None
    if hasattr(args, "scopes") and args.scopes:
        if "," in args.scopes:
            scopes = [s.strip() for s in args.scopes.split(",") if s.strip()]
        else:
            scopes = args.scopes

    if args.command == "device":
        token = get_token_device(
            callback=create_device_callback(args.quiet),
            server_url=args.server_url,
            realm=args.realm,
            client_id=args.client_id,
            auth_realm=args.auth_realm,
            scopes=scopes,
            client_factory=client_factory
        )

    elif args.command == "password":
        # Handle OTP based on arguments
        otp_code = getattr(args, "otp_code", None)
        request_otp = getattr(args, "otp", False) and not otp_code
        
        username, password, otp = get_credentials(args, request_otp=request_otp)
        
        # Use provided OTP code if available
        if otp_code:
            otp = otp_code
        
        token = get_token_password(
            username=username,
            password=password,
            otp=otp,
            server_url=args.server_url,
            realm=args.realm,
            client_id=args.client_id,
            client_secret=args.client_secret,
            auth_realm=args.auth_realm,
            scopes=scopes,
            client_factory=client_factory
        )

    elif args.command == "refresh":
        token = get_token_refresh(
            refresh_token=args.token,
            server_url=args.server_url,
            realm=args.realm,
            client_id=args.client_id,
            client_secret=args.client_secret,
            auth_realm=args.auth_realm,
            client_factory=client_factory
        )

    else:
        token = get_token_client_credentials(
            server_url=args.server_url,
            realm=args.realm,
            client_id=args.client_id,
            client_secret=args.client_secret,
            auth_realm=args.auth_realm,
            scopes=scopes,
            client_factory=client_factory
        )

    return token


def main():
    """Main entry point for CLI usage."""
    parser = init_parser()
    args = parser.parse_args()

    try:
        token = run(args)
        output = format_output(token=token, quiet=args.quiet, decode=args.decode)
        print(output)

    except AuthError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        print("\nCancelled", file=sys.stderr)
        exit(130)


if __name__ == "__main__":
    main()
