"""Client attribute certificate API methods."""
from functools import cached_property

from .base import BaseAPI
from ..generated.api.client_attribute_certificate import (
    get_admin_realms_realm_clients_client_uuid_certificates_attr,
    post_admin_realms_realm_clients_client_uuid_certificates_attr_download,
    post_admin_realms_realm_clients_client_uuid_certificates_attr_generate,
    post_admin_realms_realm_clients_client_uuid_certificates_attr_generate_and_download,
    post_admin_realms_realm_clients_client_uuid_certificates_attr_upload,
    post_admin_realms_realm_clients_client_uuid_certificates_attr_upload_certificate,
)
from ..generated.models import CertificateRepresentation, KeyStoreConfig

__all__ = (
    "ClientAttributeCertificateAPI",
    "ClientAttributeCertificateClientMixin",
    "CertificateRepresentation",
    "KeyStoreConfig",
)


class ClientAttributeCertificateAPI(BaseAPI):
    """Client attribute certificate API methods."""

    def get_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str) -> CertificateRepresentation | None:
        """Get key info for a client certificate (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name (e.g., 'jwt.credential')
            
        Returns:
            Certificate representation with key info
        """
        return self._sync(
            get_admin_realms_realm_clients_client_uuid_certificates_attr.sync,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    async def aget_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str) -> CertificateRepresentation | None:
        """Get key info for a client certificate (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name (e.g., 'jwt.credential')
            
        Returns:
            Certificate representation with key info
        """
        return await self._async(
            get_admin_realms_realm_clients_client_uuid_certificates_attr.asyncio,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    def download_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, config: dict | KeyStoreConfig) -> bytes | None:
        """Download a client certificate and private key (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            config: KeyStore configuration including format and passwords
            
        Returns:
            Certificate and private key as bytes (e.g., JKS or PKCS12 format)
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_download.sync_detailed,
            realm,
            config,
            KeyStoreConfig,
            client_uuid=client_uuid,
            attr=attr
        )
        return response.parsed

    async def adownload_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, config: dict | KeyStoreConfig) -> bytes | None:
        """Download a client certificate and private key (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            config: KeyStore configuration including format and passwords
            
        Returns:
            Certificate and private key as bytes (e.g., JKS or PKCS12 format)
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_download.asyncio_detailed,
            realm,
            config,
            KeyStoreConfig,
            client_uuid=client_uuid,
            attr=attr
        )
        return response.parsed

    def generate_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str) -> CertificateRepresentation | None:
        """Generate a new certificate with new key pair (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            
        Returns:
            New certificate representation
        """
        return self._sync(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_generate.sync,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    async def agenerate_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str) -> CertificateRepresentation | None:
        """Generate a new certificate with new key pair (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            
        Returns:
            New certificate representation
        """
        return await self._async(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_generate.asyncio,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    def generate_and_download_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, config: dict | KeyStoreConfig) -> bytes | None:
        """Generate a new certificate and download it (sync).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            config: KeyStore configuration including format and passwords
            
        Returns:
            Generated certificate and private key as bytes
        """
        response = self._sync_detailed_model(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_generate_and_download.sync_detailed,
            realm,
            config,
            KeyStoreConfig,
            client_uuid=client_uuid,
            attr=attr
        )
        return response.parsed

    async def agenerate_and_download_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, config: dict | KeyStoreConfig) -> bytes | None:
        """Generate a new certificate and download it (async).
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            config: KeyStore configuration including format and passwords
            
        Returns:
            Generated certificate and private key as bytes
        """
        response = await self._async_detailed_model(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_generate_and_download.asyncio_detailed,
            realm,
            config,
            KeyStoreConfig,
            client_uuid=client_uuid,
            attr=attr
        )
        return response.parsed

    def upload_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, file: bytes) -> CertificateRepresentation | None:
        """Upload a certificate and optionally private key (sync).
        
        NOTE: This function may not work correctly due to OpenAPI spec limitations.
        The Keycloak endpoint expects multipart/form-data with a 'file' field,
        but the OpenAPI spec doesn't document this, so the generated code doesn't support it.
        TODO: Report OpenAPI spec missing parameter multipart_data
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            file: Certificate file content as bytes (JKS or PKCS12) - CURRENTLY IGNORED
            
        Returns:
            Uploaded certificate representation
        """
        return self._sync(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_upload.sync,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    async def aupload_certificate(self, realm: str | None = None, *, client_uuid: str, attr: str, file: bytes) -> CertificateRepresentation | None:
        """Upload a certificate and optionally private key (async).
        
        NOTE: This function may not work correctly due to OpenAPI spec limitations.
        The Keycloak endpoint expects multipart/form-data with a 'file' field,
        but the OpenAPI spec doesn't document this, so the generated code doesn't support it.
        TODO: Report OpenAPI spec missing parameter multipart_data
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            file: Certificate file content as bytes (JKS or PKCS12) - CURRENTLY IGNORED
            
        Returns:
            Uploaded certificate representation
        """
        return await self._async(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_upload.asyncio,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    def upload_certificate_only(self, realm: str | None = None, *, client_uuid: str, attr: str, file: bytes) -> CertificateRepresentation | None:
        """Upload only certificate, no private key (sync).
        
        NOTE: This function may not work correctly due to OpenAPI spec limitations.
        The Keycloak endpoint expects multipart/form-data with a 'file' field,
        but the OpenAPI spec doesn't document this, so the generated code doesn't support it.
        TODO: Report OpenAPI spec missing parameter multipart_data
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            file: Certificate file content as bytes (PEM or DER format) - CURRENTLY IGNORED
            
        Returns:
            Uploaded certificate representation
        """
        return self._sync(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_upload_certificate.sync,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )

    async def aupload_certificate_only(self, realm: str | None = None, *, client_uuid: str, attr: str, file: bytes) -> CertificateRepresentation | None:
        """Upload only certificate, no private key (async).
        
        NOTE: This function may not work correctly due to OpenAPI spec limitations.
        The Keycloak endpoint expects multipart/form-data with a 'file' field,
        but the OpenAPI spec doesn't document this, so the generated code doesn't support it.
        TODO: Report OpenAPI spec missing parameter multipart_data
        
        Args:
            realm: The realm name
            client_uuid: Client UUID
            attr: Certificate attribute name
            file: Certificate file content as bytes (PEM or DER format) - CURRENTLY IGNORED
            
        Returns:
            Uploaded certificate representation
        """
        return await self._async(
            post_admin_realms_realm_clients_client_uuid_certificates_attr_upload_certificate.asyncio,
            realm,
            client_uuid=client_uuid,
            attr=attr
        )


class ClientAttributeCertificateClientMixin:
    """Mixin for BaseClientManager subclasses to be connected to the ClientAttributeCertificateAPI."""
    
    @cached_property
    def client_attribute_certificate(self) -> ClientAttributeCertificateAPI:
        """Get the ClientAttributeCertificateAPI instance."""
        return ClientAttributeCertificateAPI(manager=self)  # type: ignore[arg-type]