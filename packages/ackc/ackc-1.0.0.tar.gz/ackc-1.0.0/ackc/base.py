import asyncio
import base64
import json
import time
from typing import Awaitable, Callable

from . import env
from .api import BaseClientManager, AuthenticatedClient, Client, AuthError
from .exceptions import TokenExpiredError, InvalidTokenError

__all__ = (
    "AuthError",
    "BaseKeycloakClient",
)


class BaseKeycloakClient(BaseClientManager):
    """Base class to manage the authenticated client.
    """
    _auth_realm: str
    _client_config: dict[str, ...]
    _server_url: str
    _client_id: str
    _client_secret: str
    _token: dict | None = None
    _refresh_buffer_seconds: int

    def __init__(
            self,
            realm: str | None = None, *,
            server_url: str | None = None,
            client_id: str | None = None,
            client_secret: str | None = None,
            auth_realm: str | None = None,
            verify_ssl: bool | None = None,
            timeout: float | None = None,
            headers: dict[str, str] | None = None,
            cf_client_id: str | None = None,
            cf_client_secret: str | None = None,
            refresh_buffer_seconds: int | None = None,
            **kwds,
    ):
        """
        Initialize the Keycloak client.

        Args:
            realm: API realm to use (default: KEYCLOAK_REALM or "master")
            server_url: Keycloak server URL (default: KEYCLOAK_URL)
            client_id: OAuth2 client ID (default: KEYCLOAK_CLIENT_ID)
            client_secret: OAuth2 client secret (default: KEYCLOAK_CLIENT_SECRET)
            auth_realm: Realm to authenticate against (default: KEYCLOAK_AUTH_REALM or "master")
            verify_ssl: Whether to verify SSL certificates (default: True)
            timeout: Request timeout in seconds (default: 30.0)
            headers: Custom headers to include in requests
            cf_client_id: Cloudflare Access client ID
            cf_client_secret: Cloudflare Access client secret
            refresh_buffer_seconds: Seconds before expiry to consider token needs refresh (default: 60)
            **kwds: Additional arguments for the underlying client
        """
        super().__init__(realm=realm or env.KEYCLOAK_REALM)

        self._server_url = server_url or env.KEYCLOAK_URL
        self._client_id = client_id or env.KEYCLOAK_CLIENT_ID
        self._client_secret = client_secret or env.KEYCLOAK_CLIENT_SECRET
        self._auth_realm = auth_realm or env.KEYCLOAK_AUTH_REALM or "master"
        self._refresh_buffer_seconds = refresh_buffer_seconds or 60

        if not self._client_id or not self._client_secret:
            raise AuthError(
                "Client credentials required. "
                "Set KEYCLOAK_CLIENT_ID and KEYCLOAK_CLIENT_SECRET env vars."
            )

        cf_client_id = cf_client_id or env.CF_ACCESS_CLIENT_ID
        cf_client_secret = cf_client_secret or env.CF_ACCESS_CLIENT_SECRET

        if cf_client_id and cf_client_secret:
            headers = (headers or {}) | {
                "CF-Access-Client-Id": cf_client_id,
                "CF-Access-Client-Secret": cf_client_secret
            }

        self._client_config = {
            "base_url": self._server_url,
            "verify_ssl": verify_ssl if verify_ssl is not None else True,
            "timeout": timeout or 30.0,
            "headers": headers or {},
            **kwds
        }

    @property
    def auth_realm(self) -> str:
        """Keycloak authentication realm."""
        return self._auth_realm

    @property
    def server_url(self) -> str:
        """Keycloak server URL."""
        return self._server_url

    @property
    def client_id(self) -> str:
        """OAuth2 client ID."""
        return self._client_id

    @property
    def token(self) -> dict | None:
        """Token dict (does NOT trigger authentication).

        Use `get_token()` or `aget_token()` to ensure token retrieval.
        """
        return self._token

    @property
    def _access_token(self) -> str | None:
        """Extract access token string from token property (does NOT trigger authentication).

        Use `get_token()` or `aget_token()` to ensure token retrieval.
        """
        return self._token.get("access_token") if self._token else None

    @property
    def _refresh_token(self) -> str | None:
        """Extract refresh token string from token property (does NOT trigger authentication).

        Use `get_token()` or `aget_token()` to ensure token retrieval.
        """
        return self._token.get("refresh_token") if self._token else None

    @property
    def needs_refresh(self) -> bool:
        """Check if the internal token needs refreshing.
        
        Returns:
            True if the token needs refresh (expires within buffer), False otherwise
        """
        if not self._token:
            return True

        issued_at = self._token.get("issued_at")
        expires_in = self._token.get("expires_in")

        if issued_at is None or expires_in is None:
            return True

        current_time = time.time()
        expiry_time = issued_at + expires_in
        time_until_expiry = expiry_time - current_time

        return time_until_expiry <= self._refresh_buffer_seconds

    def _ensure_authenticated(self, scopes: list[str] | str | None = None):
        """Ensure we have a valid token and client."""
        if self._token is None:
            self._token = self._get_token(scopes)

        if self._client is None:
            self._client = AuthenticatedClient(
                token=self._access_token,
                **self._client_config
            )

    async def _ensure_authenticated_async(self, scopes: list[str] | str | None = None):
        """Ensure we have a valid token and client (async)."""
        if self._token is None:
            self._token = await self._get_token_async(scopes)

        if self._client is None:
            self._client = AuthenticatedClient(
                token=self._access_token,
                **self._client_config
            )

    def _get_token(self, scopes: list[str] | str | None = None) -> dict:
        """Get token response synchronously."""
        with Client(**self._client_config) as temp_client:
            token_url = f"{self.server_url}/realms/{self.auth_realm}/protocol/openid-connect/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
                    
            response = temp_client.get_niquests_client().post(token_url, data=data)

            if response.status_code != 200:
                raise AuthError(f"Authentication failed: {response.status_code} - {response.text}")

            return response.json()

    async def _get_token_async(self, scopes: list[str] | str | None = None) -> dict:
        """Get token response asynchronously."""
        async with Client(**self._client_config) as temp_client:
            token_url = f"{self.server_url}/realms/{self.auth_realm}/protocol/openid-connect/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
                    
            response = await temp_client.get_async_niquests_client().post(token_url, data=data)

            if response.status_code != 200:
                raise AuthError(f"Authentication failed: {response.status_code} - {response.text}")

            return response.json()

    def get_token(self, scopes: list[str] | str | None = None) -> dict:
        """Get the current token dict for this client, authenticating if necessary.
        
        Args:
            scopes: OAuth2 scopes to request
            
        Returns:
            Token dict with access_token, refresh_token, etc.
        """
        self._ensure_authenticated(scopes)
        return self._token

    async def aget_token(self, scopes: list[str] | str | None = None) -> dict:
        """Get the current token dict for this client asynchronously, authenticating if necessary.
        
        Args:
            scopes: OAuth2 scopes to request
            
        Returns:
            Token dict with access_token, refresh_token, etc.
        """
        await self._ensure_authenticated_async(scopes)
        return self._token

    def refresh_token(self):
        """Refresh this client's internal token synchronously."""
        if self._token and self._refresh_token:
            token_url = f"{self.server_url}/realms/{self.auth_realm}/protocol/openid-connect/token"
            with Client(**self._client_config) as temp_client:
                response = temp_client.get_niquests_client().post(
                    token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self._refresh_token,
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    }
                )
                if response.status_code == 400:
                    error_data = response.json()
                    if error_data.get("error") == "invalid_grant":
                        self._token = self._get_token(None)
                        if self._client:
                            self._client.token = self._access_token
                        return

                if response.status_code != 200:
                    raise AuthError(f"Token refresh failed: {response.status_code} - {response.text}")

                self._token = response.json()
                if self._client:
                    self._client.token = self._access_token
        else:
            self._token = self._get_token(None)
            if self._client:
                self._client.token = self._access_token

    async def arefresh_token(self):
        """Refresh the internal token asynchronously."""
        if self._token and self._refresh_token:
            token_url = f"{self.server_url}/realms/{self.auth_realm}/protocol/openid-connect/token"
            async with Client(**self._client_config) as temp_client:
                response = await temp_client.get_async_niquests_client().post(
                    token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self._refresh_token,
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                    }
                )
                if response.status_code == 400:
                    error_data = response.json()
                    if error_data.get("error") == "invalid_grant":
                        self._token = await self._get_token_async(None)
                        if self._client:
                            self._client.token = self._access_token
                        return

                if response.status_code != 200:
                    raise AuthError(f"Token refresh failed: {response.status_code} - {response.text}")

                self._token = response.json()
                if self._client:
                    self._client.token = self._access_token
        else:
            self._token = await self._get_token_async(None)
            if self._client:
                self._client.token = self._access_token

    def get_token_password(
        self,
        *,
        username: str,
        password: str,
        otp: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        realm: str | None = None,
        scopes: list[str] | str | None = None,
    ) -> dict:
        """Get token using password grant (legacy flow).
        
        Args:
            username: Username to authenticate
            password: Password for the user
            otp: Optional OTP/2FA code (will be concatenated with password)
            client_id: Client ID to use for authentication
            client_secret: Client secret to use for authentication
            realm: Realm to authenticate against (defaults to instance realm)
            scopes: OAuth2 scopes to request. Can be a list or space-separated string.
                   Common scopes: "openid", "profile", "email", "offline_access"

        Returns:
            Full token response dict with access_token, refresh_token, etc.
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        with Client(**self._client_config) as temp_client:
            data = {
                "grant_type": "password",
                "client_id": client_id or self._client_id,
                "username": username,
                "password": password,
                "client_secret": client_secret if client_secret is not None else (self._client_secret if client_id is None else None),
            }
            
            if otp:
                data["totp"] = otp
            
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
            
            response = temp_client.get_niquests_client().post(
                token_url,
                data=data
            )

            if response.status_code != 200:
                raise AuthError(f"Password authentication failed: {response.status_code} - {response.text}")

            return response.json()

    async def aget_token_password(
        self,
        *,
        username: str,
        password: str,
        otp: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        realm: str | None = None,
        scopes: list[str] | str | None = None,
    ) -> dict:
        """Get token using password grant (legacy flow) asynchronously.
        
        Args:
            username: Username to authenticate
            password: Password for the user
            otp: Optional OTP/2FA code (will be concatenated with password)
            client_id: Client ID to use for authentication
            client_secret: Client secret to use for authentication
            realm: Realm to authenticate against (defaults to instance realm)
            scopes: OAuth2 scopes to request. Can be a list or space-separated string.
                   Common scopes: "openid", "profile", "email", "offline_access"

        Returns:
            Full token response dict with access_token, refresh_token, etc.
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        async with Client(multiplexed=False, **self._client_config) as temp_client:
            data = {
                "grant_type": "password",
                "client_id": client_id or self._client_id,
                "username": username,
                "password": password,
                "client_secret": client_secret if client_secret is not None else (self._client_secret if client_id is None else None),
            }
            
            if otp:
                data["totp"] = otp
            
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
            
            response = await temp_client.get_async_niquests_client().post(
                token_url,
                data=data
            )

            if response.status_code != 200:
                raise AuthError(f"Password authentication failed: {response.status_code} - {response.text}")

            return response.json()

    def get_token_device(
        self,
        *,
        callback: Callable[[str, str, int], None],
        realm: str | None = None,
        client_id: str | None = None,
        scopes: list[str] | str | None = None,
    ) -> dict:
        """Get token using device authorization flow (OAuth 2.1).
        
        This implements the OAuth 2.1 Device Authorization Grant flow, which allows
        users to authenticate on a separate device (like their phone or computer).
        
        Args:
            callback: Callback function that receives keyword arguments:
                      verification_uri, user_code, expires_in (seconds)
            realm: The realm to authenticate against (defaults to instance realm)
            client_id: The client ID requesting the token (defaults to instance client_id)
            scopes: OAuth2 scopes to request. Can be a list or space-separated string.
                   Common scopes: "openid", "profile", "email", "offline_access"

        Returns:
            Full token response dict with access_token, refresh_token, etc.
            
        Raises:
            AuthError: If device flow initiation or token exchange fails
        """
        device_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/auth/device"
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        with Client(multiplexed=False, **self._client_config) as temp_client:
            data = {"client_id": client_id or self._client_id}
            
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
            
            response = temp_client.get_niquests_client().post(
                device_url,
                data=data
            )

            if response.status_code != 200:
                raise AuthError(f"Failed to start device flow: {response.status_code} - {response.text}")

            device_data = response.json()
            verification_uri = device_data.get("verification_uri_complete", device_data.get("verification_uri"))
            user_code = device_data.get("user_code")
            device_code = device_data.get("device_code")
            expires_in = device_data.get("expires_in", 600)
            interval = device_data.get("interval", 5)

            if not all([verification_uri, user_code, device_code]):
                raise AuthError("Invalid device authorization response - missing required fields")

            callback(verification_uri, user_code, expires_in)

            start_time = time.time()
            while time.time() - start_time < expires_in:
                time.sleep(interval)

                response = temp_client.get_niquests_client().post(
                    token_url,
                    data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "client_id": client_id or self._client_id,
                        "device_code": device_code,
                    }
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    error = response.json().get("error", "unknown_error")
                    if error == "authorization_pending":
                        continue
                    elif error == "slow_down":
                        interval += 5
                        continue
                    elif error == "access_denied":
                        raise AuthError("User denied authorization")
                    elif error == "expired_token":
                        raise AuthError("Device code expired")
                    else:
                        raise AuthError(f"Device flow error: {error}")
                else:
                    raise AuthError(f"Token polling failed: {response.status_code} - {response.text}")

            raise AuthError("Device authorization timed out")

    async def aget_token_device(
        self,
        *,
        callback: Callable[[str, str, int], None] | Callable[[str, str, int], Awaitable[None]],
        realm: str | None = None,
        client_id: str | None = None,
        scopes: list[str] | str | None = None,
    ) -> dict:
        """Get token using device authorization flow (OAuth 2.1) asynchronously.
        
        This implements the OAuth 2.1 Device Authorization Grant flow, which allows
        users to authenticate on a separate device (like their phone or computer).
        
        Args:
            realm: The realm to authenticate against (defaults to instance realm)
            client_id: The client ID requesting the token (defaults to instance client_id)
            scopes: OAuth2 scopes to request. Can be a list or space-separated string.
                   Common scopes: "openid", "profile", "email", "offline_access"
            callback: Callback function (sync or async) that receives keyword arguments:
                      verification_uri, user_code, expires_in (seconds)
            
        Returns:
            Full token response dict with access_token, refresh_token, etc.
            
        Raises:
            AuthError: If device flow initiation or token exchange fails
        """
        device_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/auth/device"
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        async with Client(multiplexed=False, **self._client_config) as temp_client:
            data = {"client_id": client_id or self._client_id}
            
            if scopes:
                if isinstance(scopes, list):
                    data["scope"] = " ".join(scopes)
                else:
                    data["scope"] = scopes
            
            response = await temp_client.get_async_niquests_client().post(
                device_url,
                data=data
            )

            if response.status_code != 200:
                raise AuthError(f"Failed to start device flow: {response.status_code} - {response.text}")

            device_data = response.json()
            verification_uri = device_data.get("verification_uri_complete", device_data.get("verification_uri"))
            user_code = device_data.get("user_code")
            device_code = device_data.get("device_code")
            expires_in = device_data.get("expires_in", 600)
            interval = device_data.get("interval", 5)

            if not all([verification_uri, user_code, device_code]):
                raise AuthError("Invalid device authorization response - missing required fields")

            if asyncio.iscoroutinefunction(callback):
                await callback(verification_uri, user_code, expires_in)
            else:
                callback(verification_uri, user_code, expires_in)

            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < expires_in:
                await asyncio.sleep(interval)

                response = await temp_client.get_async_niquests_client().post(
                    token_url,
                    data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "client_id": client_id or self._client_id,
                        "device_code": device_code,
                    }
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 400:
                    error = response.json().get("error", "unknown_error")
                    if error == "authorization_pending":
                        continue
                    elif error == "slow_down":
                        interval += 5
                        continue
                    elif error == "access_denied":
                        raise AuthError("User denied authorization")
                    elif error == "expired_token":
                        raise AuthError("Device code expired")
                    else:
                        raise AuthError(f"Device flow error: {error}")
                else:
                    raise AuthError(f"Token polling failed: {response.status_code} - {response.text}")

            raise AuthError("Device authorization timed out")

    def exchange_authorization_code(
        self,
        *,
        code: str,
        redirect_uri: str,
        realm: str | None = None,
    ) -> dict:
        """Exchange an authorization code for tokens.
        
        Args:
            realm: The realm to authenticate against (defaults to instance realm)
            code: The authorization code received from Keycloak
            redirect_uri: The redirect URI used in the initial authorization request
            
        Returns:
            Token dict with access_token, refresh_token, id_token, expires_in, etc.
            Includes "issued_at" timestamp added by this method.
            
        Raises:
            AuthError: If the code exchange fails
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        with Client(**self._client_config) as temp_client:
            response = temp_client.get_niquests_client().post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code != 200:
                raise AuthError(f"Authorization code exchange failed: {response.status_code} - {response.text}")

            token = response.json()
            token["issued_at"] = int(time.time())
            return token

    async def aexchange_authorization_code(
        self,
        *,
        code: str,
        redirect_uri: str,
        realm: str | None = None,
    ) -> dict:
        """Exchange an authorization code for tokens (async).
        
        Args:
            realm: The realm to authenticate against (defaults to instance realm)
            code: The authorization code received from Keycloak
            redirect_uri: The redirect URI used in the initial authorization request
            
        Returns:
            Token dict with access_token, refresh_token, id_token, expires_in, etc.
            Includes "issued_at" timestamp added by this method.
            
        Raises:
            AuthError: If the code exchange fails
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        async with Client(**self._client_config) as temp_client:
            response = await temp_client.get_async_niquests_client().post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code != 200:
                raise AuthError(f"Authorization code exchange failed: {response.status_code} - {response.text}")

            token = response.json()
            token["issued_at"] = int(time.time())
            return token

    def jwt_userinfo(self, *, jwt: str, realm: str | None = None) -> dict:
        """Get user information from an access token using Keycloak's userinfo endpoint.

        This method validates the token and returns user profile information. It's
        typically used when you need to know WHO a token belongs to.

        Args:
            jwt: The JWT string (e.g. from Authorization header)
            realm: The realm the token was issued from (defaults to instance realm)

        Returns:
            User profile dict with structure like:
            {
                "sub": "f:550e8400-e29b-41d4-a716-446655440000:johndoe",
                "email_verified": true,
                "name": "John Doe",
                "preferred_username": "johndoe",
                "given_name": "John",
                "family_name": "Doe",
                "email": "john.doe@example.com"
            }

        Raises:
            TokenExpiredError: If the token has expired
            InvalidTokenError: If the token is invalid or malformed
            AuthError: For other authentication errors
        """
        userinfo_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/userinfo"

        with Client(**self._client_config) as temp_client:
            response = temp_client.get_niquests_client().get(
                userinfo_url,
                headers={"Authorization": f"Bearer {jwt}"}
            )

            if response.status_code == 401:
                error_desc = response.json().get("error_description", "")
                if "expired" in error_desc.lower():
                    raise TokenExpiredError("Token has expired")
                raise InvalidTokenError("Invalid or malformed token")
            elif response.status_code != 200:
                raise AuthError(f"Token validation failed: {response.status_code} - {response.text}")

            return response.json()

    async def ajwt_userinfo(self, *, jwt: str, realm: str | None = None) -> dict:
        """Get user information from an access token using Keycloak's userinfo endpoint (async).

        This method validates the token and returns user profile information. It's
        typically used when you need to know WHO a token belongs to.

        Args:
            jwt: The JWT string (e.g. from Authorization header)
            realm: The realm the token was issued from (defaults to instance realm)

        Returns:
            User profile dict with structure like:
            {
                "sub": "f:550e8400-e29b-41d4-a716-446655440000:johndoe",
                "email_verified": true,
                "name": "John Doe",
                "preferred_username": "johndoe",
                "given_name": "John",
                "family_name": "Doe",
                "email": "john.doe@example.com"
            }

        Raises:
            TokenExpiredError: If the token has expired
            InvalidTokenError: If the token is invalid or malformed
            AuthError: For other authentication errors
        """
        userinfo_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/userinfo"

        async with Client(**self._client_config) as temp_client:
            response = await temp_client.get_async_niquests_client().get(
                userinfo_url,
                headers={"Authorization": f"Bearer {jwt}"}
            )

            if response.status_code == 401:
                error_desc = response.json().get("error_description", "")
                if "expired" in error_desc.lower():
                    raise TokenExpiredError("Token has expired")
                raise InvalidTokenError("Invalid or malformed token")
            elif response.status_code != 200:
                raise AuthError(f"Token validation failed: {response.status_code} - {response.text}")

            return response.json()

    def jwt_introspect(self, *, jwt: str, realm: str | None = None) -> dict:
        """Validate and get metadata about an access token.

        This method checks if a token is valid and returns detailed metadata. It's
        typically used when you need to know IF a token is valid and its properties.

        Args:
            jwt: The JWT string to validate
            realm: The realm the token was issued from (defaults to instance realm)

        Returns:
            Token metadata dict with structure like:
            {
                "active": true,  # false if token is invalid/expired
                "scope": "openid email profile",
                "username": "johndoe",
                "exp": 1735689600,  # expiration timestamp
                "iat": 1735686000,  # issued at timestamp
                "sub": "f:550e8400-e29b-41d4-a716-446655440000:johndoe",
                "aud": "my-client",
                "iss": "https://auth.example.com/realms/my-realm",
                "typ": "Bearer",
                "azp": "my-client",
                "session_state": "...",
                "client_id": "my-client",
                "token_type": "Bearer"
            }

        Raises:
            AuthError: If introspection request fails (not for invalid tokens)
        """
        introspect_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token/introspect"

        with Client(**self._client_config) as temp_client:
            response = temp_client.get_niquests_client().post(
                introspect_url,
                data={
                    "token": jwt,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code != 200:
                raise AuthError(f"Token introspection failed: {response.status_code} - {response.text}")

            return response.json()

    async def ajwt_introspect(self, *, jwt: str, realm: str | None = None) -> dict:
        """Validate and get metadata about an access token (async).

        This method checks if a token is valid and returns detailed metadata. It's
        typically used when you need to know IF a token is valid and its properties.

        Args:
            jwt: The JWT string to validate
            realm: The realm the token was issued from (defaults to instance realm)

        Returns:
            Token metadata dict with structure like:
            {
                "active": true,  # false if token is invalid/expired
                "scope": "openid email profile",
                "username": "johndoe",
                "exp": 1735689600,  # expiration timestamp
                "iat": 1735686000,  # issued at timestamp
                "sub": "f:550e8400-e29b-41d4-a716-446655440000:johndoe",
                "aud": "my-client",
                "iss": "https://auth.example.com/realms/my-realm",
                "typ": "Bearer",
                "azp": "my-client",
                "session_state": "...",
                "client_id": "my-client",
                "token_type": "Bearer"
            }

        Raises:
            AuthError: If introspection request fails (not for invalid tokens)
        """
        introspect_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token/introspect"

        async with Client(**self._client_config) as temp_client:
            response = await temp_client.get_async_niquests_client().post(
                introspect_url,
                data={
                    "token": jwt,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code != 200:
                raise AuthError(f"Token introspection failed: {response.status_code} - {response.text}")

            return response.json()

    def jwt_refresh(self, *, refresh_token: str, realm: str | None = None) -> dict:
        """Exchange a refresh token for new tokens.

        Args:
            refresh_token: The refresh token to exchange
            realm: The realm to authenticate against (defaults to instance realm)

        Returns:
            New token dict with access_token, refresh_token, expires_in, etc.
            Includes "issued_at" timestamp added by this method.

        Raises:
            TokenExpiredError: If the refresh token has expired
            AuthError: If the refresh fails for other reasons
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        with Client(**self._client_config) as temp_client:
            response = temp_client.get_niquests_client().post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == "invalid_grant":
                    raise TokenExpiredError("Refresh token has expired or is invalid")

            if response.status_code != 200:
                raise AuthError(f"Token refresh failed: {response.status_code} - {response.text}")

            token = response.json()
            token["issued_at"] = int(time.time())
            return token

    async def ajwt_refresh(self, *, refresh_token: str, realm: str | None = None) -> dict:
        """Exchange a refresh token for new tokens (async).

        Args:
            refresh_token: The refresh token to exchange
            realm: The realm to authenticate against (defaults to instance realm)

        Returns:
            New token dict with access_token, refresh_token, expires_in, etc.
            Includes "issued_at" timestamp added by this method.

        Raises:
            TokenExpiredError: If the refresh token has expired
            AuthError: If the refresh fails for other reasons
        """
        token_url = f"{self.server_url}/realms/{realm or self.realm}/protocol/openid-connect/token"

        async with Client(**self._client_config) as temp_client:
            response = await temp_client.get_async_niquests_client().post(
                token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                }
            )

            if response.status_code == 400:
                error_data = response.json()
                if error_data.get("error") == "invalid_grant":
                    raise TokenExpiredError("Refresh token has expired or is invalid")

            if response.status_code != 200:
                raise AuthError(f"Token refresh failed: {response.status_code} - {response.text}")

            token = response.json()
            token["issued_at"] = int(time.time())
            return token

    @classmethod
    def jwt_decode(cls, *, jwt: str) -> dict:
        """Decode JWT and return claims without validation.

        This method performs client-side JWT decoding to extract claims.
        It does NOT validate the token signature or check if it's still valid.
        For server-side validation, use jwt_userinfo() or jwt_introspect().

        Args:
            jwt: The JWT string to decode

        Returns:
            Decoded JWT claims as a dict

        Raises:
            InvalidTokenError: If the JWT is malformed or cannot be decoded
        """
        try:
            parts = jwt.split(".")
            if len(parts) != 3:
                raise InvalidTokenError("JWT must have 3 parts separated by dots")

            payload = parts[1]
            payload += "=" * (-len(payload) % 4)
            decoded = base64.urlsafe_b64decode(payload)
            return json.loads(decoded)

        except (ValueError, json.JSONDecodeError) as e:
            raise InvalidTokenError(f"Failed to decode JWT: {e}")
        except Exception as e:
            raise InvalidTokenError(f"JWT decoding error: {e}")

    @classmethod
    def jwt_needs_refresh(cls, *, jwt: str, buffer_seconds: int = 60) -> bool:
        """Check if a JWT token needs refreshing by decoding and checking expiry.
        
        Args:
            jwt: The JWT string to check
            buffer_seconds: Seconds before expiry to consider it "needs refresh" (default: 60)
            
        Returns:
            True if the token expires within buffer_seconds, False otherwise
            
        Raises:
            InvalidTokenError: If the JWT is malformed or cannot be decoded
        """
        try:
            claims = cls.jwt_decode(jwt=jwt)

            exp = claims.get("exp")
            if exp is None:
                raise InvalidTokenError("JWT missing \"exp\" claim")

            current_time = time.time()
            time_until_expiry = exp - current_time

            return time_until_expiry <= buffer_seconds
        except InvalidTokenError:
            raise
        except Exception as e:
            raise InvalidTokenError(f"JWT validation error: {e}")
