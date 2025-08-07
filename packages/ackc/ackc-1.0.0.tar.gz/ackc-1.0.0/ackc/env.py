"""Environment variable handling for ACKC with prefix support."""
import os
from functools import cached_property


class EnvSettings:
    """Environment settings with optional prefix support via KEYCLOAK_ENV_PREFIX."""

    def __init__(self):
        self._prefix = os.getenv("KEYCLOAK_ENV_PREFIX")
        if self._prefix and not self._prefix.endswith("_"):
            self._prefix = self._prefix + "_"

    def _setting(self, name: str, dflt: str | None = None) -> str | None:
        """Get setting with prefix support."""
        if self._prefix:
            prefixed_name = self._prefix + name
            value = os.getenv(prefixed_name)

            if value is not None:
                return value

        return os.getenv(name, dflt)

    @cached_property
    def KEYCLOAK_URL(self) -> str | None:
        return self._setting("KEYCLOAK_URL")

    @cached_property
    def KEYCLOAK_MANAGEMENT_URL(self) -> str | None:
        return self._setting("KEYCLOAK_MANAGEMENT_URL")

    @cached_property
    def KEYCLOAK_REALM(self) -> str | None:
        return self._setting("KEYCLOAK_REALM")

    @cached_property
    def KEYCLOAK_AUTH_REALM(self) -> str | None:
        return self._setting("KEYCLOAK_AUTH_REALM", self.KEYCLOAK_REALM)

    @cached_property
    def KEYCLOAK_CLIENT_ID(self) -> str | None:
        return self._setting("KEYCLOAK_CLIENT_ID")

    @cached_property
    def KEYCLOAK_CLIENT_SECRET(self) -> str | None:
        return self._setting("KEYCLOAK_CLIENT_SECRET")

    @cached_property
    def CF_ACCESS_CLIENT_ID(self) -> str | None:
        return self._setting("CF_ACCESS_CLIENT_ID")

    @cached_property
    def CF_ACCESS_CLIENT_SECRET(self) -> str | None:
        return self._setting("CF_ACCESS_CLIENT_SECRET")


env_settings = EnvSettings()


def __dir__():
    """https://peps.python.org/pep-0562/"""
    return [attr for attr in dir(env_settings) if not attr.startswith("_")]


def __getattr__(name):
    """https://peps.python.org/pep-0562/"""
    return getattr(env_settings, name)


__all__ = tuple(__dir__())
